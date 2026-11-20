import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import {ROOT} from '../scripts/model.mjs';
import {build,main,python,validateOutput} from '../scripts/cli.mjs';
import {available} from '../scripts/pptxgen.mjs';
const fixture=path.join(ROOT,'tests/fixtures/dbscan.json');
const run=(exe,args,cwd)=>new Promise((resolve,reject)=>{
  const log=path.join(fs.mkdtempSync(path.join(os.tmpdir(),'slides-test-log-')),'log');
  const fd=fs.openSync(log,'w');
  const p=spawn(exe,args,{cwd,stdio:['ignore',fd,fd]});
  const cleanup=()=>{fs.closeSync(fd);const text=fs.readFileSync(log,'utf8');fs.rmSync(path.dirname(log),{recursive:true,force:true});return text;};
  p.on('error',error=>{cleanup();reject(error);});
  p.on('close',code=>{const text=cleanup();code===0?resolve(text):reject(new Error(text));});
});
test('fluxo real: 12 PPTX/PDF/PNG, notas, extração, revisão, falhas e reprodução portátil', {timeout:240000}, async t=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'slides-creator-test-'));
  t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const out=path.join(temp,'deck');
  const result=await build({spec:fixture,out,backend:'ooxml','pdf-engine':'native'});
  assert.equal(result.slides,12);assert.equal(result.status,'needs-visual-review');
  const qa=JSON.parse(fs.readFileSync(path.join(out,'qa.json')));
  assert.deepEqual(qa.issues,[]);assert.equal(qa.pdfPages,12);assert.equal(qa.previewCount,12);
  assert.ok(fs.readFileSync(path.join(out,'notes.md'),'utf8').includes('DBSCAN'));
  const source=path.join(out,'source');
  assert.ok(fs.existsSync(path.join(source,'assets/input/figure-10.svg')));
  const extracted=await python('extract',{input:path.join(out,'presentation.pdf'),out:path.join(temp,'extracted')});
  assert.ok(fs.readFileSync(extracted.text,'utf8').includes('Página 12'));
  const md=path.join(temp,'notes.md');fs.writeFileSync(md,'# Ensaio\n\nFonte em Markdown.');
  const request=await main(['prepare','--prompt','Crie 12 slides de um seminário','--input',md,'--out',path.join(temp,'request')]);
  assert.equal(request.prompt,'Crie 12 slides de um seminário');assert.ok(request.source.characters>0);
  await assert.rejects(build({spec:fixture,out,backend:'ooxml'}),/já existe/);
  // Exercise review bookkeeping without claiming actual visual inspection by a test.
  const reviewFile=path.join(temp,'review.json');
  fs.writeFileSync(reviewFile,JSON.stringify({status:'unavailable',pages:[],issues:[],reviewer:'Automated test',method:'No visual claim; exercising explicit unavailable state.'}));
  const reviewed=await main(['review','--out',out,'--file',reviewFile]);
  assert.equal(reviewed.status,'visual-review-unavailable');
  fs.writeFileSync(reviewFile,JSON.stringify({status:'passed',pages:[1],issues:[],reviewer:'test',method:'Invalid incomplete declaration'}));
  await assert.rejects(main(['review','--out',out,'--file',reviewFile]),/todas as páginas/);
  const first=fs.readdirSync(path.join(out,'previews')).find(f=>f.endsWith('.png'));
  fs.unlinkSync(path.join(out,'previews',first));
  assert.equal((await validateOutput(out)).status,'failed');
  // Reproduction must work from copied code, different CWD, and copied image assets.
  const reproduced=path.join(temp,'reproduced');
  await run(process.execPath,['scripts/cli.mjs','build','--spec','deck.json','--out',reproduced,'--backend','ooxml','--pdf-engine','native'],source);
  assert.equal(JSON.parse(fs.readFileSync(path.join(reproduced,'qa.json'))).previewCount,12);
  // Deliberately broken OPC relationship is detected, even with a valid ZIP CRC.
  const corrupt=path.join(temp,'broken.pptx');
  await run('python3',['-c','import zipfile,sys\nwith zipfile.ZipFile(sys.argv[1]) as src, zipfile.ZipFile(sys.argv[2],"w") as dst:\n for name in src.namelist():\n  if name!="ppt/slides/slide2.xml": dst.writestr(name,src.read(name))',path.join(out,'presentation.pptx'),corrupt]);
  const bad=await python('integrity',{pptx:corrupt,scene:path.join(out,'scene.json')});
  assert.ok(bad.issues.some(i=>i.code==='broken-relationship'));
  const invalid=JSON.parse(fs.readFileSync(fixture));invalid.slides[1].bullets=['texto muito longo '.repeat(1000)];
  invalid.slides[9].path=path.join(ROOT,'assets/graphics/pipeline.svg');
  const invalidFile=path.join(temp,'invalid.json');fs.writeFileSync(invalidFile,JSON.stringify(invalid));
  await assert.rejects(build({spec:invalidFile,out:path.join(temp,'invalid-output'),backend:'ooxml'}),/Layout reprovado/);
  assert.ok(!fs.existsSync(path.join(temp,'invalid-output/presentation.pptx')));
  // Verify portable installation without touching the user's home.
  const installed=path.join(temp,'project/.agents/skills/slides-creator');
  await run(process.execPath,[path.join(ROOT,'scripts/install.mjs'),'--dest',installed],temp);
  const portableOut=path.join(temp,'portable-output');
  await run(process.execPath,['scripts/cli.mjs','build','--spec','tests/fixtures/dbscan.json','--out',portableOut,'--backend','ooxml','--pdf-engine','native'],installed);
  assert.equal(JSON.parse(fs.readFileSync(path.join(portableOut,'qa.json'))).previewCount,12);
});
test('backend PptxGenJS: integração real quando a dependência está instalada', {skip:!available(),timeout:120000},async t=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'slides-pptxgen-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const r=await build({spec:fixture,out:path.join(temp,'deck'),backend:'pptxgenjs'});
  assert.equal(r.backend,'pptxgenjs');assert.equal(r.slides,12);
});
