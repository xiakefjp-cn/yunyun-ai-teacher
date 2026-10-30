/* Actual browser recording, no simulated network or test results. */
const fs=require('node:fs'); const path=require('node:path');
const {chromium}=require(process.env.YUNYUN_PLAYWRIGHT || 'C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..'), out=path.join(root,'deliverables');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const config=process.env.YUNYUN_DEMO_URL ? {url:process.env.YUNYUN_DEMO_URL,workspace:path.join(root,'demo_evidence/recording-workspace')} : JSON.parse(fs.readFileSync(path.join(root,'demo_evidence/desktop-workspace/.yunyun/desktop.json'),'utf8'));
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:960},recordVideo:{dir:out,size:{width:1440,height:960}},acceptDownloads:true});
 const page=await context.newPage(); const video=page.video(); const steps=[];
 const start=Date.now(); const pause=ms=>new Promise(r=>setTimeout(r,ms));
 async function step(title){steps.push({seconds:Math.round((Date.now()-start)/1000),title});console.log(title); await page.screenshot({path:path.join(out,`step-${steps.length}.png`)});await pause(2500)}
 async function ready(){await page.waitForFunction(()=>!document.getElementById('generate').disabled,{},{timeout:240000})}
 page.on('dialog',d=>d.accept());
 await page.goto(config.url); await page.waitForSelector('#workspace');
 await page.locator('#live').selectOption('true');
 await page.locator('#request').fill('给初二备一节40分钟的循环结构课，刚学完条件语句；40人中5人未提交、3人写了死循环、6人有边界错误。按协议输出教案、2个示例、3道分层题及参考答案评分点。');
 await step('1. 教师提出需求，选择真实 qwen-plus API，工作区为本机真实目录');
 await page.locator('#generate').click();await ready();
 if(!await page.locator('#notice').innerText().then(t=>t.includes('全部通过')))throw Error(await page.locator('#notice').innerText());
 await step('2. 真实API返回；全部示例和参考解已真实执行');
 await page.locator('#warnings').scrollIntoViewIfNeeded();await step('3. 班情驱动的错因预警：证据、触发原因和干预');
 const cards=page.locator('#items > article');await cards.nth(0).scrollIntoViewIfNeeded();await step('4. 结构化教案和40分钟课堂安排');
 await cards.nth(1).scrollIntoViewIfNeeded();await step('5. 课堂示例代码及输入、期望、真实输出');
 await cards.nth(5).scrollIntoViewIfNeeded();await step('6. 分层挑战题、参考答案、评分点与边界用例');
 const whileBox=page.locator('#code_example_while'); const original=await whileBox.inputValue();
 const bad=original.replace(/^\s*i\s*\+=\s*1\s*$/m,'');
 // If the model chose other names, use a known deliberate infinite-loop mutation.
 await whileBox.fill('n = int(input())\ni = 1\nwhile i <= n:\n    print(i)\n');
 await whileBox.locator('..').getByRole('button',{name:'保存修改并重新验证'}).click();await ready();
 if(!await page.locator('#notice').innerText().then(t=>t.includes('验证失败')))throw Error('Expected failure gate');
 await page.locator('#code_example_while').scrollIntoViewIfNeeded();await step('7. 故意删去变量更新：真实执行超限，定位失败用例');
 await page.locator('#download').click();await ready();await step('8. 失败时下载被系统阻止');
 await page.locator('#history button').first().click();await ready();await step('9. 恢复验证通过的修订，审核状态清空');
 for(let i=0;i<6;i++){await cards.nth(i).getByRole('button',{name:'接受',exact:true}).click();await ready()}
 await page.locator('#publish').click();await ready();await page.locator('dialog').waitFor();await step('10. 正式写入前展示完整 diff，由教师确认');
 await page.locator('#commit').click();await ready();await step('11. 教案包已真实写入本机 published 目录');
 const downloaded=page.waitForEvent('download');await page.locator('#download').click();const download=await downloaded;await download.saveAs(path.join(out,'课堂教案包.zip'));await ready();
 await page.reload();await page.waitForFunction(()=>document.getElementById('notice').textContent.includes('已接受 6/6'));
 await step('12. 刷新恢复会话、审核状态和历史；可下载教案包');
 const state=await page.evaluate(async()=>await(await api('state')).json());
 fs.writeFileSync(path.join(out,'browser-acceptance.json'),JSON.stringify({steps,workspace:config.workspace,mode:state.mode,verified:state.state.current.verified,accepted:state.state.accepted,revisionCount:state.state.revisions.length,pages:await page.locator('#items article').count(),durationSeconds:Math.round((Date.now()-start)/1000)},null,2));
 await context.close();const videoPath=await video.path();fs.renameSync(videoPath,path.join(out,'耘耘AI助教-完整演示.webm'));await browser.close();
 console.log('PASS: desktop workspace, live API, failure gate, rollback, review, real publish and download; video saved.');
})().catch(e=>{console.error(e);process.exit(1)});
