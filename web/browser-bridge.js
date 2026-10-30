const browserWorker=new Worker('browser-worker.js');let sequence=0;const waiting=new Map();
browserWorker.onmessage=({data})=>{const entry=waiting.get(data.id);if(!entry)return;clearTimeout(entry.timer);waiting.delete(data.id);if(data.error){entry.reject(Error(data.error));return;}try{localStorage.setItem('yunyun-browser-session',JSON.stringify(data.saved));}catch(e){entry.reject(Error('浏览器保存空间不足，请先下载教案包'));return;}entry.resolve(data.result)};
browserWorker.onerror=e=>{for(const entry of waiting.values()){clearTimeout(entry.timer);entry.reject(Error('Python运行环境加载失败，请检查网络后刷新页面'));}waiting.clear()};
async function api(path,data){
 const result=await new Promise((resolve,reject)=>{const id=++sequence;const timer=setTimeout(()=>{browserWorker.terminate();reject(Error('运行超时，已停止执行。刷新后可恢复上次已保存会话。'));},120000);waiting.set(id,{resolve,reject,timer});let saved;try{saved=JSON.parse(localStorage.getItem('yunyun-browser-session')||'null')}catch(e){}browserWorker.postMessage({id,payload:{route:path,data,saved}})});
 if(path==='download'){const bytes=Uint8Array.from(atob(result.zip),c=>c.charCodeAt(0));return new Response(bytes,{headers:{'Content-Type':'application/zip'}})}
 return {json:async()=>result};
}
