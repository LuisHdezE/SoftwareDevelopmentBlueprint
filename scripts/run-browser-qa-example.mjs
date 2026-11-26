import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
const html=await readFile(new URL('../templates/browser-qa.example/index.html',import.meta.url));
const server=createServer((req,res)=>{if(req.url!=='/'){res.writeHead(404);res.end();return;}res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html);});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
let browser, executed=0;
try {
 browser=await chromium.launch({headless:true});
 for(const viewport of [{width:1280,height:800},{width:375,height:812}]){
  const context=await browser.newContext({viewport});
  const page=await context.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  try{
   await page.goto('http://127.0.0.1:'+server.address().port+'/');
   assert.equal(await page.getByRole('heading',{name:'Reference items'}).count(),1);executed++;
   await page.getByRole('button',{name:'Add item'}).click();
   assert.equal(await page.getByRole('alert').innerText(),'Name required');executed++;
   await page.getByLabel('Item name').fill('Synthetic item');
   await page.getByRole('button',{name:'Add item'}).click();
   assert.equal(await page.getByRole('listitem').innerText(),'Synthetic item');executed++;
   assert.equal(await page.getByRole('status').innerText(),'1 item(s)');executed++;
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);executed++;
   assert.deepEqual(errors,[]);executed++;
  }finally{await context.close();}
 }
 console.log(JSON.stringify({scope:'synthetic_browser_only',runner:'playwright',browser:browser.version(),viewports:2,executed,failures:0}));
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve));}
