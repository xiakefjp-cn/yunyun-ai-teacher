const fs=require('node:fs');
const {chromium}=require(process.env.YUNYUN_PLAYWRIGHT || 'C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}), errors=[];
  page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
  await page.goto((process.argv[2]||'http://127.0.0.1:8773')+'/studio.html');
  await page.waitForFunction(()=>document.getElementById('workspace').textContent.length>0,null,{timeout:120000});
  await page.selectOption('#subject','语文');
  await page.locator('#generate').click();
  await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('材料填写检查完成'),null,{timeout:120000});
  if(await page.locator('textarea.code').count())throw Error('Language material has code editors');
  if(!await page.locator('#notice').innerText().then(t=>t.includes('待教师核对')))throw Error('Missing scope');
  const ref=process.env.YUNYUN_REFERENCE;
  if(ref){
   await page.locator('#reference-file').setInputFiles(ref);
   await page.waitForFunction(()=>document.getElementById('reference').value.includes('卡牌'));
   if(await page.locator('#reference').inputValue().then(t=>t.includes('执教人：')))throw Error('Author line not removed');
   if(await page.locator('#subject').inputValue()!=='语文')throw Error('Import reset subject');
  }
  const download=page.waitForEvent('download');
  await page.locator('#all').click();await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('已接受 6/6'));
  await page.locator('#download').click();const file=await download;
  fs.mkdirSync('deliverables',{recursive:true});await file.saveAs('deliverables/language-browser.zip');
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'deliverables/subject-language.png',fullPage:false});
  await page.selectOption('#subject','数学');
  await page.locator('#generate').click();
  await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('列出算式核对通过'),null,{timeout:120000});
  const result=await page.evaluate(async()=>{
   const s=(await(await api('state')).json()).state;
   if(s.current.bundle.subject!=='数学')throw Error('Wrong math subject');
   const good=s.current.id,item=s.current.bundle.items.find(x=>x.id==='basic');
   let bad=await(await api('edit',{id:'basic',answer:item.answer,calculations:[{expression:'3*4',expected:'13'}]})).json();
   if(bad.current.verified)throw Error('Wrong arithmetic escaped');
   let blocked=false;try{await api('download',{})}catch(e){blocked=true}if(!blocked)throw Error('Math export gate failed');
   await api('rollback',{id:good});await refresh();
   return {languageScope:'completeness only',mathGate:blocked,mathChecks:s.current.reports.reduce((n,r)=>n+r.cases.length,0)};
  });
  await page.evaluate(()=>window.scrollTo(0,0));await page.screenshot({path:'deliverables/subject-math.png'});
  await page.reload();await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('数学'),null,{timeout:120000});
  await page.selectOption('#subject','信息科技');await page.locator('#generate').click();
  await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('配套用例全部通过'),null,{timeout:120000});
  if(!await page.locator('textarea.code').count())throw Error('Coding editor missing');
  if(errors.length)throw Error(errors.join(';'));
  result.codingRestored=true;result.wordImported=Boolean(ref);
  fs.writeFileSync('deliverables/subjects-browser.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
