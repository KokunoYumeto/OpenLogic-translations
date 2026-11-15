"""Windows process-tree limits and the shared, nonblocking TeX mutex.

Every child starts suspended, enters its capped job, and only then resumes.
No console window, shell, detached child or uncapped fallback is used.
"""
import ctypes as C
from ctypes import wintypes as W
import os
import mmap
from pathlib import Path
import subprocess
import time

TEX_MUTEX = r'Global\InterlanguageTeXSlotV1'
MEMORY_LIMIT = 5_000_000_000


class BasicLimits(C.Structure):
    _fields_ = [('process_time',C.c_int64),('job_time',C.c_int64),('flags',W.DWORD),
                ('min_ws',C.c_size_t),('max_ws',C.c_size_t),('processes',W.DWORD),
                ('affinity',C.c_size_t),('priority',W.DWORD),('scheduling',W.DWORD)]


class IOCounters(C.Structure):
    _fields_ = [(name,C.c_uint64) for name in ('reads','writes','others','read_bytes','write_bytes','other_bytes')]


class ExtendedLimits(C.Structure):
    _fields_ = [('basic',BasicLimits),('io',IOCounters),('process_memory',C.c_size_t),
                ('job_memory',C.c_size_t),('peak_process',C.c_size_t),('peak_job',C.c_size_t)]


class Accounting(C.Structure):
    _fields_ = [(name,C.c_int64) for name in ('user','kernel','period_user','period_kernel')]+[
        (name,W.DWORD) for name in ('faults','total','active','terminated')]


class Security(C.Structure):
    _fields_ = [('size',W.DWORD),('descriptor',C.c_void_p),('inherit',W.BOOL)]


class Startup(C.Structure):
    _fields_ = [('size',W.DWORD),('reserved',W.LPWSTR),('desktop',W.LPWSTR),('title',W.LPWSTR),
                ('x',W.DWORD),('y',W.DWORD),('width',W.DWORD),('height',W.DWORD),
                ('cols',W.DWORD),('rows',W.DWORD),('fill',W.DWORD),('flags',W.DWORD),
                ('show',W.WORD),('reserved_size',W.WORD),('reserved_ptr',C.c_void_p),
                ('stdin',W.HANDLE),('stdout',W.HANDLE),('stderr',W.HANDLE)]


class ProcessInfo(C.Structure):
    _fields_ = [('process',W.HANDLE),('thread',W.HANDLE),('pid',W.DWORD),('tid',W.DWORD)]


def kernel():
    if os.name!='nt':
        raise ValueError('guarded compilation currently requires Windows; no uncapped fallback')
    k = C.WinDLL('kernel32',use_last_error=True)
    signatures = {
        'CreateMutexW':([C.c_void_p,W.BOOL,W.LPCWSTR],W.HANDLE),
        'WaitForSingleObject':([W.HANDLE,W.DWORD],W.DWORD),
        'ReleaseMutex':([W.HANDLE],W.BOOL), 'CloseHandle':([W.HANDLE],W.BOOL),
        'CreateJobObjectW':([C.c_void_p,W.LPCWSTR],W.HANDLE),
        'SetInformationJobObject':([W.HANDLE,C.c_int,C.c_void_p,W.DWORD],W.BOOL),
        'QueryInformationJobObject':([W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p],W.BOOL),
        'AssignProcessToJobObject':([W.HANDLE,W.HANDLE],W.BOOL),
        'TerminateJobObject':([W.HANDLE,W.UINT],W.BOOL),
        'TerminateProcess':([W.HANDLE,W.UINT],W.BOOL),
        'GetExitCodeProcess':([W.HANDLE,C.POINTER(W.DWORD)],W.BOOL),
        'CreateFileW':([W.LPCWSTR,W.DWORD,W.DWORD,C.POINTER(Security),W.DWORD,W.DWORD,W.HANDLE],W.HANDLE),
        'CreateProcessW':([W.LPCWSTR,W.LPWSTR,C.c_void_p,C.c_void_p,W.BOOL,W.DWORD,
                           C.c_void_p,W.LPCWSTR,C.POINTER(Startup),C.POINTER(ProcessInfo)],W.BOOL),
        'ResumeThread':([W.HANDLE],W.DWORD),
    }
    for name,(args,result) in signatures.items():
        fn=getattr(k,name);fn.argtypes=args;fn.restype=result
    return k


def checked(value,operation):
    if not value:
        raise OSError(C.get_last_error(),operation+' failed')
    return value


class TeXSlot:
    def __init__(self,name=TEX_MUTEX):
        self.k=kernel();self.name=name;self.handle=None;self.acquired=False;self.abandoned=False

    def __enter__(self):
        self.handle=checked(self.k.CreateMutexW(None,False,self.name),'CreateMutex')
        result=self.k.WaitForSingleObject(self.handle,0)
        if result in (0,0x80):
            self.acquired=True;self.abandoned=result==0x80
        elif result!=0x102:
            self.k.CloseHandle(self.handle);self.handle=None
            raise OSError(C.get_last_error(),'TeX mutex acquisition failed')
        return self

    def __exit__(self,*args):
        if self.handle:
            try:
                if self.acquired:checked(self.k.ReleaseMutex(self.handle),'ReleaseMutex')
            finally:
                self.k.CloseHandle(self.handle);self.handle=None


def run_job(arguments,cwd,log,env=None,timeout=240,memory_limit=MEMORY_LIMIT):
    """Execute one tool in a hidden capped job and wait for all descendants."""
    if not arguments or timeout<=0 or not 0<memory_limit<=MEMORY_LIMIT:
        raise ValueError('invalid guarded process limits or command')
    exe=str(Path(arguments[0]).resolve())
    if not Path(exe).is_file():raise ValueError('guarded executable absent')
    k=kernel();job=None;output=None;stdin=None;info=ProcessInfo();started=time.monotonic()
    resumed=False;peak=0;timed_out=False
    def active():
        accounting=Accounting()
        checked(k.QueryInformationJobObject(job,1,C.byref(accounting),C.sizeof(accounting),None),'QueryJobAccounting')
        return accounting.active
    try:
        job=checked(k.CreateJobObjectW(None,None),'CreateJobObject')
        limits=ExtendedLimits();limits.basic.flags=0x2000|0x200;limits.job_memory=memory_limit
        checked(k.SetInformationJobObject(job,9,C.byref(limits),C.sizeof(limits)),'SetJobMemoryLimit')
        actual=ExtendedLimits()
        checked(k.QueryInformationJobObject(job,9,C.byref(actual),C.sizeof(actual),None),'ReadJobMemoryLimit')
        # Windows rounds the byte limit down to a page boundary (5e9 -> 4999999488).
        if actual.job_memory!=memory_limit//mmap.PAGESIZE*mmap.PAGESIZE or actual.basic.flags&0x2200!=0x2200:
            raise ValueError('process-tree cap was not installed')
        sa=Security(C.sizeof(Security),None,True)
        Path(log).parent.mkdir(parents=True,exist_ok=True)
        output=k.CreateFileW(str(Path(log).resolve()),0x40000000,1,C.byref(sa),2,0,None)
        stdin=k.CreateFileW('NUL',0x80000000,3,C.byref(sa),3,0,None)
        invalid=C.c_void_p(-1).value
        if output==invalid or stdin==invalid:raise OSError(C.get_last_error(),'process log or NUL open failed')
        si=Startup();si.size=C.sizeof(si);si.flags=0x100;si.stdin=stdin;si.stdout=output;si.stderr=output
        command=C.create_unicode_buffer(subprocess.list2cmdline([exe,*map(str,arguments[1:])]))
        environment=C.create_unicode_buffer('\0'.join(k+'='+v for k,v in sorted((env or os.environ).items(),key=lambda x:x[0].casefold()))+'\0\0')
        checked(k.CreateProcessW(exe,command,None,None,True,0x08000004|0x400,environment,
                                  str(Path(cwd).resolve()),C.byref(si),C.byref(info)),'CreateSuspendedProcess')
        if not k.AssignProcessToJobObject(job,info.process):
            error=C.get_last_error();k.TerminateProcess(info.process,125);k.WaitForSingleObject(info.process,10000)
            raise OSError(error,'Suspended child was not captured; it never ran')
        if k.ResumeThread(info.thread)==0xffffffff:
            raise OSError(C.get_last_error(),'Resume captured process failed')
        resumed=True
        while active():
            if time.monotonic()-started>timeout:
                timed_out=True;checked(k.TerminateJobObject(job,124),'TerminateTimedOutJob');break
            time.sleep(0.05)
        # The lock stays held until the entire job, not only its leader, exits.
        deadline=time.monotonic()+10
        while active() and time.monotonic()<deadline:time.sleep(0.05)
        if active():raise RuntimeError('capped process tree did not terminate within ten seconds')
        code=W.DWORD();checked(k.GetExitCodeProcess(info.process,C.byref(code)),'GetExitCodeProcess')
        checked(k.QueryInformationJobObject(job,9,C.byref(actual),C.sizeof(actual),None),'ReadJobPeakMemory')
        peak=actual.peak_job
        return {'exit_code':int(code.value),'timed_out':timed_out,'seconds':round(time.monotonic()-started,3),
                'process_id':int(info.pid),'memory_limit_bytes':memory_limit,
                'enforced_job_memory_bytes':int(actual.job_memory),
                'peak_job_memory_bytes':int(peak),'started_suspended':True,'captured_before_resume':True,
                'all_descendants_exited':True}
    finally:
        if job:
            k.TerminateJobObject(job,125)
        if info.process:
            # If assignment/resume failed, a suspended leader is terminated too.
            if not resumed:k.TerminateProcess(info.process,125)
            k.WaitForSingleObject(info.process,10000)
        for handle in (info.thread,info.process,job,output,stdin):
            if handle and handle!=C.c_void_p(-1).value:k.CloseHandle(handle)
