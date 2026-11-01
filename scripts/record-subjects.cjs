/* Real interaction with a local service; offline samples are explicitly labelled. */
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.YUNYUN_PLAYWRIGHT||'C:/Users/Fan jun pu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
(async()=>{
 fs.mkdirSync('deliverables/subject-videos',{recursive:true});
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},recordVideo:{dir:'deliverables/subject-videos',size:{width:1440,height:1000}},acceptDownloads:true});
 const page=await context.newPage(),video=page.video(),steps=[],start=Date.now();
 page.on('dialog',d=>d.accept());
 async function ready(){await page.waitForFunction(()=>!document.getElementById('generate').disabled,null,{timeout:120000})}
 async function step(title){steps.push({seconds:Math.round((Date.now()-start)/1000),title});console.log(title);await page.waitForTimeout(2400)}
 await page.goto(process.env.YUNYUN_DEMO_URL||'http://127.0.0.1:8879');
 await step('1. 多学科产品首页，进入体验');
 await page.getByRole('link',{name:'体验产品能力',exact:false}).first().click();await ready();
 await page.selectOption('#subject','语文');await page.locator('#generate').click();await ready();
 if(!await page.locator('#notice').innerText().then(t=>t.includes('材料填写检查完成')))throw Error('Language scope missing');
 await step('2. 语文jqx：示范、分层活动、材料填写检查，读音书写由老师判断');
 await page.locator('#items article').nth(3).scrollIntoViewIfNeeded();await step('3. 语文参考答案与教师观察点，可以直接修改文字');
 await page.evaluate(()=>window.scrollTo(0,0));await page.selectOption('#subject','数学');await page.locator('#generate').click();await ready();
 await page.locator('#items article').nth(3).scrollIntoViewIfNeeded();await step('4. 数学乘法：题意、答案、评分点和可核对算式');
 await page.locator('#calc_basic').fill(JSON.stringify([{expression:'4*3',expected:'13'}]));
 await page.locator('#items article').nth(3).getByRole('button',{name:'保存修改并重新检查',exact:true}).click();await ready();
 if(!await page.locator('#notice').innerText().then(t=>t.includes('检查失败')))throw Error('Math error escaped');
 await step('5. 故意把4乘3的期望写成13，程序算出12并标出失败');
 await page.locator('#download').click();await ready();await page.locator('#notice').scrollIntoViewIfNeeded();await step('6. 存在计算错误时，教案下载被阻止');
 await page.evaluate(()=>window.scrollTo(0,0));await page.selectOption('#subject','信息科技');await page.locator('#generate').click();await ready();
 const cards=page.locator('#items article');
 await cards.nth(2).locator('details').evaluateAll(ds=>ds.forEach(d=>d.open=true));await cards.nth(2).scrollIntoViewIfNeeded();
 await step('7. 信息科技循环课：Python示例真实运行，查看输入输出');
 const good=await page.evaluate(()=>state.current.id);
 await page.locator('#code_example_while').fill('while True:\n    pass\n');
 await cards.nth(2).getByRole('button',{name:'保存修改并重新验证',exact:true}).click();await ready();
 if(!await page.locator('#notice').innerText().then(t=>t.includes('验证失败')))throw Error('Loop escaped');
 await step('8. 故意写死循环，实际执行超限');
 await page.locator('#download').click();await ready();await page.locator('#notice').scrollIntoViewIfNeeded();await step('9. 代码错误时，同样禁止导出');
 await page.locator('.side-details').evaluate(d=>d.open=true);
 await page.locator(`#history button[onclick="rollback('${good}')"]`).click();await ready();
 await page.locator('#all').click();await ready();
 await page.locator('#publish').click();await ready();await page.locator('dialog').waitFor();await step('10. 老师确认6项材料，保存前查看文件修改');
 await page.locator('#commit').click();await ready();
 const downloaded=page.waitForEvent('download');await page.locator('#download').click();await(await downloaded).saveAs('deliverables/multisubject-classroom.zip');await ready();
 await step('11. 教案真实写入本机目录，并下载完整教案包');
 const workspace=(await page.evaluate(async()=>await(await api('state')).json())).workspace;
 if(!fs.existsSync(path.join(workspace,'published/lesson.md')))throw Error('Published host lesson missing');
 const evidence={steps,durationSeconds:Math.round((Date.now()-start)/1000),language:'completeness only',mathFailureBlocked:true,loopFailureBlocked:true,localFiles:true,source:'explicit offline samples'};
 fs.writeFileSync('deliverables/subjects-video.json',JSON.stringify(evidence,null,2));
 await context.close();fs.copyFileSync(await video.path(),'deliverables/yunyun-multisubject.webm');await browser.close();
 console.log(JSON.stringify(evidence));
})().catch(e=>{console.error(e);process.exit(1)});
