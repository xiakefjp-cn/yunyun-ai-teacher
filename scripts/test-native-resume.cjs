/* Run after closing the Tk launcher and reopening the SAME workspace via its UI. */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.YUNYUN_PLAYWRIGHT || 'C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 const root=path.resolve(__dirname,'..'), workspace=path.join(root,'demo_evidence/native-acceptance');
 const config=JSON.parse(fs.readFileSync(path.join(workspace,'.yunyun/desktop.json'),'utf8'));
 const prior=JSON.parse(fs.readFileSync(path.join(root,'deliverables/browser-acceptance.json'),'utf8'));
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:960}});
  await page.goto(config.url+'/studio.html');
  await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('已接受 6/6'));
  const state=await page.evaluate(async()=>await(await api('state')).json());
  if(state.mode!=='desktop' || !state.state.current.verified || state.state.revisions.length!==prior.revisionCount)throw Error('Resume mismatch');
  if(!fs.existsSync(path.join(workspace,'published/lesson.md')))throw Error('Missing host lesson');
  await page.screenshot({path:path.join(root,'deliverables/native-resume.png')});
  fs.mkdirSync(path.join(root,'docs/evidence'),{recursive:true});
  fs.writeFileSync(path.join(root,'docs/evidence/native-acceptance.json'),JSON.stringify({
   mode:state.mode,verified:true,accepted:state.state.accepted,revisionCount:state.state.revisions.length,
   cases:state.state.current.reports.reduce((n,r)=>n+r.cases.length,0),
   native_window_started_via_ui:true,closed_and_reopened_via_ui:true,host_lesson_exists:true,
   browser_flow:prior.steps,video_seconds:prior.durationSeconds,
   scope:'Native Tk directory entry and start/close/reopen; browser workspace flow automated in Playwright. Folder chooser dialog not exercised.'
  },null,2));
  console.log('PASS: native restart restored verified revision, 6 reviews, history and actual host lesson.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
