"""Resolve an assembled OLP book's imports and native selection before conversion.

The result is an intermediate TeX stream, not an HTML reader. It retains native
math, tokens, labels and front/back-matter commands for the converter. There is
no TeX execution, translation, network access or implicit English fallback.
"""
from pathlib import Path, PurePosixPath
import posixpath
import re

from .assembly import digest, json_bytes
from .build import verify_assembly
from .cache import relative_path
from .macrophases import group, skip_space, mask_comments
from .selective import SelectionState, Selector, token
from .sourceexport import ABOUT


def body_only(text):
    code = mask_comments(text)
    start = re.search(r'\\begin\s*\{document\}', code)
    end = re.search(r'\\end\s*\{document\}', code)
    if bool(start) != bool(end):
        raise ValueError('incomplete subfile document wrapper')
    if start:
        if end.start() < start.end(): raise ValueError('reversed document wrapper')
        # Preserve original source line/character locations in selection receipts.
        return ''.join('\n' if c == '\n' else ' ' for c in text[:start.end()]) + text[start.end():end.start()]
    return text


class BookProjection:
    def __init__(self, source, assembly, imports, *, mark_units=False):
        self.source = Path(source).resolve()
        self.assembly = assembly
        verify_assembly(self.source, assembly)
        if assembly.get('unreconciled_legacy_inputs'):
            raise ValueError('unreconciled legacy inputs')
        self.book = assembly['book_directory']
        self.locale = assembly['locale']
        relative_path(self.book); relative_path(self.locale)
        self.units = {u['path']:u for u in assembly['units']}
        self.expected = dict((p, uid) for uid,p in imports)
        self.inputs = {}; self.order = []; self.stack = []; self.snippets = {}
        self.selector = Selector(self.command, self.environment)
        self.hooks = {'OLEndChapterHook':[], 'OLEndPartHook':[]}
        self.chapter = 0; self.appendix = False
        self.defer = False; self.problems = []; self.deferred_records = []; self.flushes = []
        self.configuration = False
        self.mark_units = mark_units

    def read(self, path):
        relative_path(path)
        if path not in self.assembly['files']:
            raise ValueError('unrecorded projection input: ' + path)
        data = (self.source/path).read_bytes()
        if digest(data) != self.assembly['files'][path]['sha256']:
            raise ValueError('projection input changed: ' + path)
        self.inputs[path] = {'sha256':digest(data), 'bytes':len(data)}
        return data.decode('utf-8-sig')

    def snippet(self, text, state, parent, kind):
        identity = parent + '#' + kind + '-' + digest(text.encode())[:16]
        self.snippets[identity] = {'parent':parent, 'kind':kind, 'sha256':digest(text.encode())}
        return self.selector.project(text, state, identity)

    def expand(self, path, state, section=None):
        if path in self.stack or len(self.stack) > 64:
            raise ValueError('recursive source import: ' + path)
        original = self.read(path)
        self.stack.append(path)
        try:
            result = self.selector.project(body_only(original),state,path)
        finally:
            self.stack.pop()
        return result if section is None else (r'\begingroup\def\ol@sectioncs{' + section + '}\n' + result + '\n' + r'\endgroup')

    def chapter_label(self):
        if self.appendix:
            if not 1 <= self.chapter <= 26: raise ValueError('unsupported appendix counter')
            return chr(64 + self.chapter)
        return str(self.chapter)

    def book_path(self, value):
        value = value.replace(r'\thechapter', self.chapter_label())
        if '\\' in value: raise ValueError('unresolved book input: ' + value)
        path = posixpath.normpath(posixpath.join(self.book,value))
        if not path.endswith('.tex'): path += '.tex'
        relative_path(path)
        if not path.startswith(self.book + '/'):
            raise ValueError('book input escapes book directory')
        return path

    def command(self, name, text, pos, state, source):
        if name in ('preto','appto'):
            hook, p, _ = token(text,pos); value,end = group(text,p)
            if hook not in ('\\' + n for n in self.hooks):
                raise ValueError('unsupported executable book hook: ' + hook)
            record = (value, source)
            if name == 'preto': self.hooks[hook[1:]].insert(0,record)
            else: self.hooks[hook[1:]].append(record)
            return '',end
        if self.configuration:
            return None
        if name == 'olimport':
            p = pos; star = text[p:p+1] == '*'
            if star: p += 1
            p = skip_space(text,p); directory = None
            if text[p:p+1] == '[': directory,p = group(text,p,'[',']')
            value,p = group(text,p); section = 'section'; p = skip_space(text,p)
            if text[p:p+1] == '[': section,p = group(text,p,'[',']')
            if not re.fullmatch(r'[A-Za-z]+',section): raise ValueError('unsafe section selector')
            if value == ABOUT:
                target = 'content/open-logic-about.tex'
            else:
                if '\\' in value or '\\' in (directory or ''):
                    raise ValueError('unresolved corpus import expression')
                actual_source = self.stack[-1]
                prefix = 'locale/' + self.locale + '/'
                canonical = actual_source[len(prefix):] if actual_source.startswith(prefix) else actual_source
                base = 'content' if star and directory is not None else str(PurePosixPath(canonical).parent)
                target = posixpath.normpath(posixpath.join(base,directory or '',value))
                if not target.endswith('.tex'): target += '.tex'
            relative_path(target)
            if target not in self.expected:
                raise ValueError('executed import outside recorded book scope: ' + target)
            unit = self.units[target]
            if unit['id'] != self.expected[target] or unit['state'] != 'current' or unit['english_fill']:
                raise ValueError('uncurrent or English-filled imported unit: ' + target)
            path = 'locale/' + self.locale + '/' + target
            self.order.append({'unit':unit['id'],'path':target,'assembled_path':path,
                               'sha256':self.assembly['files'][path]['sha256'],'section':section})
            row = self.order[-1]
            if self.mark_units:
                # Identify the actual executed import, including repeated imports.
                # Empty inline anchors add no prose or mathematical content.
                row['html_id'] = 'olp-unit-' + str(len(self.order)).zfill(6)
            expanded = self.expand(path,state.copy(),section)
            if self.mark_units:
                expanded = r'\hypertarget{' + row['html_id'] + '}{}' + expanded
            return expanded,p
        if name in ('input','include'):
            value,end = group(text,pos)
            expanded=self.expand(self.book_path(value),state)
            # TeX reads the file after tokenizing the surrounding control words.
            # Serializing its bytes must not fuse \textbf + Gedhene into a new
            # command, or a final imported command with following source text.
            start=pos-len(name)-1
            if re.search(r'\\[A-Za-z@]+$',text[:start]) and re.match(r'[A-Za-z@]',expanded):
                expanded=' '+expanded
            if re.search(r'\\[A-Za-z@]+$',expanded) and re.match(r'[A-Za-z@]',text[end:]):
                expanded+=' '
            return expanded,end
        if name == 'IfFileExists':
            value,p = group(text,pos); yes,p = group(text,p); no,end = group(text,p)
            path = self.book_path(value); chosen = path in self.assembly['files']
            return self.snippet(yes if chosen else no,state,source,'file-choice'),end
        if name in ('mainmatter','appendix'):
            if self.problems: raise ValueError('unflushed exercises at matter boundary')
            self.chapter = 0; self.appendix = name == 'appendix'
            return '\\' + name,pos
        if name in ('chapter','olchapter'):
            p = skip_space(text,pos); starred = text[p:p+1] == '*'
            if starred: p += 1
            p = skip_space(text,p); optional = ''
            if text[p:p+1] == '[':
                value,p = group(text,p,'[',']')
                optional = '[' + self.snippet(value,state.copy(),source,'short-heading') + ']'
            args=[]
            for _ in range(3 if name == 'olchapter' else 1):
                value,p = group(text,p);args.append(value)
            if not starred:
                if self.problems: raise ValueError('unflushed exercises before next chapter')
                self.chapter += 1
            selected = ['{' + self.snippet(value,state.copy(),source,'heading') + '}' for value in args]
            return '\\' + name + ('*' if starred else '') + optional + ''.join(selected),p
        if name in ('olfileid','olchapterid','olpartid'):
            p = skip_space(text,pos)
            if text[p:p+1] == '[': _,p = group(text,p,'[',']')
            keys = ['theolpart','theolchapter','theolsection'][:{'olfileid':3,'olchapterid':2,'olpartid':1}[name]]
            for key in keys:
                value,p = group(text,p); state.context[key]=value
            return '\\'+name+text[pos:p],p
        if name == 'problemsperchapter':
            self.defer = True; return '',pos
        if name == 'stopproblems':
            if self.problems: raise ValueError('unflushed exercises at stopproblems')
            self.defer = False; return '',pos
        if name in self.hooks:
            parts=[self.snippet(value,state,origin,'hook-'+name) for value,origin in self.hooks[name]]
            if name == 'OLEndChapterHook' and self.problems:
                parts.append(r'\section*{\problemsname}\addcontentsline{toc}{section}{\problemsname}')
                label = self.chapter_label()
                parts.append(r'\renewcommand*{\probch}{' + label + r'}\setcounter{probd}{0}')
                for problem in self.problems:
                    if problem['tags'] != state.tags:
                        raise ValueError('deferred problem tag state differs from capture; replay required')
                    context=''.join('\\renewcommand*{\\'+k+'}{'+v+'}' for k,v in problem['context'].items())
                    parts.append(r'\begingroup'+context+r'\begin{probd}'+problem['body']+r'\end{probd}\endgroup')
                    self.deferred_records.append({k:v for k,v in problem.items() if k not in ('body','tags')}
                        | {'chapter':label,'number':len([r for r in self.deferred_records if r['chapter']==label])+1})
                self.flushes.append({'chapter':label,'problems':len(self.problems),'after_summary':True})
                self.problems=[]
            return '\n'.join(parts),pos
        return None

    def environment(self, env, start, body, end, state, source):
        if env in ('prob','probtag') and self.defer:
            tag_argument = None
            if env == 'probtag':
                # The pinned native defer style explicitly discards this argument;
                # imposing a new tag filter here would change the PDF's contents.
                tag_argument, after = group(body,0)
                body = body[after:]
            self.problems.append({'source':source,'body':body,'body_sha256':digest(body.encode()),
                                  'context':dict(state.context),'tags':dict(state.tags),
                                  'native_ignored_probtag_argument':tag_argument})
            return ''
        return None

    def project(self, entry, configuration_paths):
        state = SelectionState()
        defer_style = self.read('sty/open-logic-defer.sty')
        if r'\renewenvironment{probdeferredtag}[2]{\begin{probd}}{\end{probd}}' not in defer_style:
            raise ValueError('unrecognized native deferred exercise semantics')
        for path in ('sty/open-logic-selective.sty','sty/open-logic-referencing.sty'):
            self.read(path)
        self.configuration = True
        try:
            for path in configuration_paths:
                self.selector.project(self.read(path),state,path)
        finally:
            self.configuration = False
        initial = {'tags':dict(state.tags),'excluded_environments':sorted(state.excluded)}
        output = self.expand(self.book + '/' + entry,state)
        if self.problems: raise ValueError('unflushed exercises at book end')
        seen = {row['path'] for row in self.order}
        if seen != set(self.expected):
            raise ValueError('book projection differs from import lock: missing=' + repr(sorted(set(self.expected)-seen))
                             + '; extra=' + repr(sorted(seen-set(self.expected))))
        return output, {'schema':'olpkit.book-projection.v1','assembly_sha256':digest(json_bytes(self.assembly)),
            'initial_selection':initial,
            'inputs':self.inputs,'unit_order':self.order,'unique_units':len(seen),'unit_occurrences':len(self.order),
            'selection_events':self.selector.events,'snippets':self.snippets,'deferred_exercises':self.deferred_records,
            'unit_markers':self.mark_units,
            'exercise_flushes':self.flushes,'projected_sha256':digest(output.encode()),'tex_runs':0,
            'reader_complete':False,'remaining':['tokens and mathematical macros','PDF numbering and cross-references',
                'front matter, glossary, bibliography and photo credits','figures and HTML/EPUB conversion']}
