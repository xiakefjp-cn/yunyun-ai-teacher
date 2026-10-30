const fs=require('node:fs');const path=require('node:path');
const {chromium}=require('C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
try{
 const page=await browser.newPage();const url=process.argv[2]||'http://127.0.0.1:8771';
 await page.goto(url);
 await page.getByRole('link',{name:'体验产品能力',exact:false}).first().click();
 await page.waitForURL('**/studio.html');
 await page.waitForFunction(()=>document.getElementById('workspace').textContent.includes('浏览器'),{},{timeout:120000});
 fs.mkdirSync('deliverables',{recursive:true});await page.screenshot({path:'deliverables/redesign-empty.png'});
 const result=await page.evaluate(async()=>{
  const stats={total:40,missing:5,infinite_loop:3,boundary:6};
  let s=await(await api('generate',{request:'循环结构',stage:'初中',stats,live:false})).json();
  if(!s.current.verified)throw Error('Browser code verification failed');const good=s.current.id;
  const cases=s.current.reports.reduce((n,r)=>n+r.cases.length,0);
  s=await(await api('generate',{request:'故意失败',stage:'初中',stats,live:false})).json();
  if(s.current.verified)throw Error('Infinite loop escaped verification');
  let blocked=false;try{await api('download',{})}catch(e){blocked=e.message.includes('交付前')}
  if(!blocked)throw Error('Download gate failed');
  s=await(await api('rollback',{id:good})).json();
  for(const x of s.current.bundle.items)await api('review',{id:x.id,accept:true});
  const bytes=new Uint8Array(await(await api('download',{})).arrayBuffer());
  if(bytes[0]!==80||bytes[1]!==75)throw Error('ZIP is invalid');
  const adapted=await(await api('generate',{request:'大学循环结构',stage:'大学',stats:{total:35,missing:0,infinite_loop:0,boundary:2},live:false})).json();
  if(!adapted.current.verified||adapted.current.bundle.stage!=='大学')throw Error('Stage adaptation failed');
  await refresh();
  return {cases,blocked,zipBytes:bytes.length,stage:adapted.current.bundle.stage,revisionCount:adapted.revisions.length};
 });
 await page.reload();await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('全部通过'),{},{timeout:120000});
 result.restored=await page.locator('#history button').count()>=3;
 if(!result.restored)throw Error('Resume failed');
 fs.mkdirSync('deliverables',{recursive:true});fs.writeFileSync('deliverables/pages-acceptance.json',JSON.stringify({url,...result},null,2));
 await page.screenshot({path:'deliverables/public-demo.png',fullPage:true});await page.screenshot({path:'deliverables/redesign-result.png'});console.log(JSON.stringify(result));
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
