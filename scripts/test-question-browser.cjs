const fs=require('node:fs');
const {chromium}=require(process.env.YUNYUN_PLAYWRIGHT||'C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
 await page.goto((process.argv[2]||'http://127.0.0.1:8765')+'/studio.html');
 await page.waitForFunction(()=>document.getElementById('workspace').textContent.length>0,null,{timeout:120000});
 await page.selectOption('#subject','信息科技');await page.selectOption('#live','false');
 await page.locator('#bank-search').locator('..').evaluate(d=>d.open=true);await page.locator('#bank-search').click();
 await page.waitForFunction(()=>document.querySelectorAll('#bank-list input').length>=3);
 await page.locator('#bank-import').setInputFiles('docs/题库导入示例.json');
 await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('已导入1题'));
 await page.locator('#bank-search').click();await page.locator('[data-bank-id="teacher-demo-basic"]').check();
 await page.locator('#generate').click();await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('配套用例全部通过'),null,{timeout:120000});
 if(!await page.locator('#items').innerText().then(t=>t.includes('teacher-demo-basic')&&t.includes('解题思路')))throw Error('Missing provenance or solution');
 const result=await page.evaluate(async()=>{
  let s=(await(await api('state')).json()).state;
  if(s.current.bundle.question_sources.basic.bank_id!=='teacher-demo-basic')throw Error('Wrong selected question');
  const code=s.current.bundle.items.find(x=>x.id==='basic').code;
  s=await(await api('edit',{id:'basic',code:code+'\n'})).json();
  if(s.current.bundle.question_sources.basic.kind!=='teacher_edited')throw Error('Edit not labelled');
  for(const x of s.current.bundle.items)await api('review',{id:x.id,accept:true});
  const bytes=new Uint8Array(await(await api('download',{})).arrayBuffer());if(bytes[0]!==80||bytes[1]!==75)throw Error('Missing ZIP');
  await refresh();return {bankSelected:true,customImport:true,editProvenance:true,zipBytes:bytes.length};
 });
 await page.evaluate(()=>window.scrollTo(0,0));fs.mkdirSync('deliverables',{recursive:true});await page.screenshot({path:'deliverables/question-modes.png'});
 await page.reload();await page.waitForFunction(()=>document.getElementById('workspace').textContent.length>0,null,{timeout:120000});
 const restored=await page.evaluate(async()=>((await(await api('question-bank',{subject:'信息科技',stage:'初中',topic:'循环结构'})).json()).questions.some(q=>q.id==='teacher-demo-basic')));
 if(!restored||errors.length)throw Error(errors.join(';')||'Import not persisted');
 console.log(JSON.stringify({...result,importPersisted:true}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
