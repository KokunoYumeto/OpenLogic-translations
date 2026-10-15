'use strict';
// No network service, analytics, rewriting, or omitted spine items.
(async()=>{
const $=id=>document.getElementById(id),digits=n=>String(n).replace(/\d/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d]);
const status=$('status'),toc=$('toc'),panel=$('contents');let book,rendition,current=null,busy=false,pending=null;
const fail=e=>{status.textContent='بازکردن این بخش ناموفق بود. می‌توانید EPUB کامل را از صفحهٔ انتشار دریافت کنید.';console.error(e);window.readerFailure=String(e)};
try{
 const bytes=Uint8Array.from(atob(window.OPENLOGIC_BOOK_BASE64),c=>c.charCodeAt(0));delete window.OPENLOGIC_BOOK_BASE64;
 book=ePub(bytes.buffer,{openAs:'binary'});await book.opened;await book.ready;
 const nav=await book.loaded.navigation,flatten=items=>items.flatMap(x=>[x,...flatten(x.subitems||[])]),entries=flatten(nav.toc);
 const order=book.spine.spineItems.filter(s=>!s.href.endsWith('nav.xhtml'));
 rendition=book.renderTo('book',{width:'100%',height:'100%',flow:'scrolled-doc',manager:'default',allowScriptedContent:false});
 window.readerBook=book;window.readerRendition=rendition;
 const clean=s=>s.replace(/\s*[—–]\s*OLP-\d{4}\/(?:FOL|PROP)\s*$/,'').trim();
 let previous='دیباچه';
 const rows=entries.map(e=>{let label=clean(e.label);if(/^OLP-/.test(label))label='ادامهٔ '+previous;else previous=label;return{...e,label,technical:e.label}});
 function update(href){current=order.findIndex(s=>s.href===href);const row=rows.find(r=>r.href.split('#')[0]===href);status.textContent=(row?.label||'متن کتاب')+' — بخش '+digits(current+1)+' از '+digits(order.length);$('previous').disabled=current<=0;$('next').disabled=current<0||current>=order.length-1;}
 async function display(href){if(busy){pending=href;return;}busy=true;status.textContent='در حال بازکردن بخش…';try{await rendition.display(href);panel.hidden=true;$('show-toc').setAttribute('aria-expanded','false');const location=rendition.currentLocation();if(location?.start?.href)update(location.start.href);history.replaceState(null,'','#read='+encodeURIComponent(href));}catch(e){fail(e)}finally{busy=false;if(pending){const next=pending;pending=null;display(next)}}}
 for(const row of rows){const li=document.createElement('li'),a=document.createElement('a');a.textContent=row.label;a.href='#read='+encodeURIComponent(row.href);a.title=row.technical;a.addEventListener('click',e=>{e.preventDefault();display(row.href)});li.dataset.search=(row.label+' '+row.technical).toLocaleLowerCase('fa');li.append(a);toc.append(li)}
 $('count').textContent=digits(rows.length)+' مدخل؛ همهٔ بخش‌های منبع و یادداشت‌های ویرایش در دسترس‌اند.';
 $('show-toc').onclick=()=>{panel.hidden=!panel.hidden;$('show-toc').setAttribute('aria-expanded',String(!panel.hidden));if(!panel.hidden)$('find').focus()};
 $('find').oninput=()=>{const q=$('find').value.trim().toLocaleLowerCase('fa');for(const li of toc.children)li.hidden=!li.dataset.search.includes(q)};
 $('previous').onclick=()=>{if(current>0)display(order[current-1].href)};$('next').onclick=()=>{if(current>=0&&current<order.length-1)display(order[current+1].href)};
 $('about').disabled=false;$('about').onclick=()=>display('about.xhtml#about');
 $('font-size').onchange=()=>rendition.themes.fontSize($('font-size').value);
 rendition.on('relocated',loc=>{if(loc?.start?.href)update(loc.start.href)});
 rendition.on('displayError',fail);
 window.addEventListener('keydown',e=>{if(e.key==='Escape'){panel.hidden=true;$('show-toc').setAttribute('aria-expanded','false')}});
 window.addEventListener('hashchange',()=>{if(location.hash.startsWith('#read='))display(decodeURIComponent(location.hash.slice(6)))});
 let first=rows[0].href;
 if(location.hash.startsWith('#read=')){const requested=decodeURIComponent(location.hash.slice(6));if(order.some(s=>s.href===requested.split('#')[0]))first=requested;}
 await display(first);window.readerReady={spineItems:order.length,tocItems:rows.length};
}catch(e){fail(e)}
})();
