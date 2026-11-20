#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import { ROOT, checkLayout, profileKey, profiles } from './model.mjs';
import { compile } from './layout.mjs';
import { available, writePptx } from './pptxgen.mjs';

const json=(file,value)=>fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');
const read=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
export async function python(command, args={}) {
  const input=[path.join(ROOT,'scripts/office.py'),command];
  for(const [k,v] of Object.entries(args)) input.push(`--${k}`,String(v));
  return new Promise((resolve,reject)=>{
    const child=spawn(process.env.PYTHON || 'python3',input,{stdio:['ignore','pipe','pipe'],env:{...process.env,LC_ALL:'C.UTF-8'}});
    let stdout='',stderr='';
    const timer=setTimeout(()=>{ child.kill('SIGTERM'); reject(new Error('Python excedeu 240 segundos')); },240000);
    child.stdout.setEncoding('utf8'); child.stderr.setEncoding('utf8');
    child.stdout.on('data',data=>{ stdout+=data; if(stdout.length>16*1024*1024) child.kill('SIGTERM'); });
    child.stderr.on('data',data=>{ stderr=(stderr+data).slice(-65536); });
    child.on('error',error=>{clearTimeout(timer);reject(error);});
    child.on('close',code=>{
      clearTimeout(timer);
      if(code!==0) return reject(new Error(stderr.trim()||`Python encerrou com ${code}`));
      try {resolve(JSON.parse(stdout));} catch(error) {reject(new Error('Resposta inválida do helper Python: '+error.message));}
    });
  });
}
function parse(args) {
  const [command,...rest]=args, opts={};
  for(let i=0;i<rest.length;i++) {
    if(!rest[i].startsWith('--')) throw new Error(`Argumento inválido: ${rest[i]}`);
    const k=rest[i].slice(2);
    if(k==='force') opts[k]=true;
    else { if(!rest[i+1] || rest[i+1].startsWith('--')) throw new Error(`Valor ausente: --${k}`); opts[k]=rest[++i]; }
  }
  const allowed={doctor:[],profiles:[],extract:['input','out'],prepare:['prompt','input','out','profile','theme'],build:['spec','out','profile','theme','backend','pdf-engine','force'],validate:['out'],review:['out','file']};
  if(!allowed[command]) throw new Error('Use doctor, profiles, prepare, extract, build, validate ou review; veja references/usage.md');
  for(const k of Object.keys(opts)) if(!allowed[command].includes(k)) throw new Error(`Opção desconhecida: --${k}`);
  if(opts.theme&&opts.profile&&profileKey(opts.theme)!==profileKey(opts.profile)) throw new Error('--theme e --profile devem indicar o mesmo tema');
  return {command,opts};
}
function outputDir(target, force) {
  if(!target) throw new Error('--out obrigatório');
  const out=path.resolve(target);
  if(out===ROOT || ROOT.startsWith(out+path.sep) || out===os.homedir()) throw new Error('Diretório de saída inseguro');
  if(fs.existsSync(out) && fs.readdirSync(out).length) {
    if(!force || !fs.existsSync(path.join(out,'.slides-creator-output'))) throw new Error('Saída já existe. Use uma pasta nova ou --force em saída desta ferramenta.');
    // Delete only generated artifacts, preserving arbitrary files added by a user.
    for(const name of ['presentation.pptx','presentation.pdf','previews','source','qa.json','scene.json','layout.json','plan.json','visual-review.json','notes.md']) {
      fs.rmSync(path.join(out,name),{recursive:true,force:true});
    }
  }
  fs.mkdirSync(out,{recursive:true}); fs.writeFileSync(path.join(out,'.slides-creator-output'),'1\n');
  return out;
}
function bundle(spec, base, out, engine) {
  const target=path.join(out,'source'); fs.mkdirSync(target,{recursive:true});
  fs.cpSync(path.join(ROOT,'scripts'),path.join(target,'scripts'),{recursive:true,filter:src=>!src.includes('__pycache__')});
  fs.cpSync(path.join(ROOT,'assets'),path.join(target,'assets'),{recursive:true});
  for(const folder of ['references','tests']) if(fs.existsSync(path.join(ROOT,folder))) fs.cpSync(path.join(ROOT,folder),path.join(target,folder),{recursive:true});
  if(fs.existsSync(path.join(ROOT,'SKILL.md'))) fs.copyFileSync(path.join(ROOT,'SKILL.md'),path.join(target,'SKILL.md'));
  if(fs.existsSync(path.join(ROOT,'agents'))) fs.cpSync(path.join(ROOT,'agents'),path.join(target,'agents'),{recursive:true});
  fs.copyFileSync(path.join(ROOT,'package.json'),path.join(target,'package.json'));
  if(fs.existsSync(path.join(ROOT,'package-lock.json'))) fs.copyFileSync(path.join(ROOT,'package-lock.json'),path.join(target,'package-lock.json'));
  const copy=structuredClone(spec);
  copy.slides.forEach((s,i)=>{
    if(s.layout!=='figure') return;
    const src=path.resolve(base,s.path), name=`figure-${i+1}${path.extname(src)}`;
    fs.mkdirSync(path.join(target,'assets/input'),{recursive:true});
    fs.copyFileSync(src,path.join(target,'assets/input',name)); s.path=`assets/input/${name}`;
  });
  const copyImage=(obj,key,name)=>{
    if(!obj?.[key]) return;
    const src=path.resolve(base,obj[key]),dest=`assets/input/${name}${path.extname(src)}`;
    fs.mkdirSync(path.join(target,'assets/input'),{recursive:true});
    fs.copyFileSync(src,path.join(target,dest));obj[key]=dest;
  };
  copyImage(copy.visual,'duckPath','mascot');
  copy.slides.forEach((s,i)=>{
    copyImage(s,'duckPath',`mascot-${i+1}`);
    copyImage(s,'coverLogo',`cover-logo-${i+1}`);
  });
  json(path.join(target,'deck.json'),copy);
  fs.writeFileSync(path.join(target,'reproduce.txt'),`A partir desta pasta:\nnode scripts/cli.mjs build --spec deck.json --out ../reproduced --backend ooxml --pdf-engine ${engine==='native-subset'?'native':'auto'}\n\nPara PptxGenJS: npm install --no-audit --no-fund e omita --backend.\n`);
}
function fingerprint(out) {
  const digest=createHash('sha256');
  const names=['scene.json','presentation.pptx','presentation.pdf',...fs.readdirSync(path.join(out,'previews')).filter(f=>/^slide-.*\.png$/.test(f)).sort().map(f=>'previews/'+f)];
  for(const name of names) digest.update(name).update(fs.readFileSync(path.join(out,name)));
  return digest.digest('hex');
}
export async function validateOutput(out) {
  out=path.resolve(out);
  const scene=read(path.join(out,'scene.json'));
  const layout=checkLayout(scene);
  const actual=await python('validate',{pptx:path.join(out,'presentation.pptx'),scene:path.join(out,'scene.json'),pdf:path.join(out,'presentation.pdf'),previews:path.join(out,'previews')});
  const previous=fs.existsSync(path.join(out,'qa.json'))?read(path.join(out,'qa.json')):{};
  const visual=fs.existsSync(path.join(out,'visual-review.json'))?read(path.join(out,'visual-review.json')):{status:'pending',pages:[],issues:[]};
  const issues=[...layout,...actual.issues];
  const complete=visual.status==='passed' && visual.pages.length===scene.slides.length && visual.issues.length===0 && visual.fingerprint===fingerprint(out);
  const status=issues.length?'failed':complete?'passed':visual.status==='unavailable'?'visual-review-unavailable':'needs-visual-review';
  const qa={...previous,status,backend:previous.backend||'unknown',generatedAt:previous.generatedAt||new Date().toISOString(),validatedAt:new Date().toISOString(),
    ...actual,issues,visualReview:visual,checks:[...actual.checks,'scene bounds','overlap','text fit estimate','font minimum','contrast'],
    limitations:['Text fit uses conservative font metrics, not a typography engine.','PDF text presence does not prove text is fully visible.','Visual review is a reviewer declaration; no automatic image understanding.','Reference existence and scientific accuracy require source review.']};
  if(previous.backend==='ooxml') qa.limitations.push('Bar charts are editable native shapes; PptxGenJS uses native PowerPoint charts.');
  if(previous.conversion?.engine==='native-subset') qa.limitations.push(previous.conversion.limitation);
  if(scene.fonts) {qa.fonts=scene.fonts;qa.limitations.push(...scene.fonts.warnings);}
  json(path.join(out,'qa.json'),qa); return qa;
}
export async function build(opts) {
  if(!opts.spec) throw new Error('--spec obrigatório');
  const source=path.resolve(opts.spec), spec=read(source);
  if(opts.theme&&opts.profile&&profileKey(opts.theme)!==profileKey(opts.profile)) throw new Error('--theme e --profile devem indicar o mesmo tema');
  if(opts.theme||opts.profile) spec.plan.profile=profileKey(opts.theme||opts.profile);
  const scene=compile(spec,path.dirname(source));
  const layout=checkLayout(scene);
  const issues=layout;
  let backend=opts.backend || (available()?'pptxgenjs':'ooxml');
  if(!['pptxgenjs','ooxml'].includes(backend)) throw new Error('--backend: pptxgenjs ou ooxml');
  if(backend==='pptxgenjs'&&!available()) throw new Error('PptxGenJS não instalado; execute npm install ou selecione --backend ooxml');
  if(path.resolve(opts.out||'')===path.dirname(source) || source.startsWith(path.resolve(opts.out||'')+path.sep)) throw new Error('Coloque deck.json fora da pasta de saída para permitir regeneração segura');
  const out=outputDir(opts.out,opts.force);
  json(path.join(out,'scene.json'),scene); json(path.join(out,'plan.json'),{title:spec.title,...spec.plan});
  json(path.join(out,'layout.json'),{issues,method:'Bounding boxes, contrast and conservative line metrics',autoCorrections:['Word wrapping applied before measuring; font sizes never reduced']});
  let qa={status:'failed',backend,generatedAt:new Date().toISOString(),issues}; json(path.join(out,'qa.json'),qa);
  if(issues.length) throw new Error(`Layout reprovado: ${issues.length} problemas; veja ${out}/layout.json`);
  try {
    const pptx=path.join(out,'presentation.pptx');
    if(backend==='pptxgenjs') await writePptx(scene,pptx);
    else await python('write',{scene:path.join(out,'scene.json'),out:pptx});
    const integrity=await python('integrity',{scene:path.join(out,'scene.json'),pptx});
    if(integrity.issues.length) throw new Error('Integridade reprovada: '+JSON.stringify(integrity.issues));
    const converted=await python('convert',{pptx,out,engine:opts['pdf-engine']||'auto'});
    qa.conversion=converted; json(path.join(out,'qa.json'),qa);
    const rendered=await python('render',{pdf:converted.pdf,out:path.join(out,'previews')});
    const html='<!doctype html><html lang="'+esc(spec.plan.language)+'"><meta charset="utf-8"><title>'+esc(spec.title)+'</title><style>body{background:#e5e7eb;font-family:sans-serif;margin:2rem}figure{max-width:1100px;margin:2rem auto}img{width:100%;box-shadow:0 2px 12px #999}figcaption{padding:.5rem}</style><h1>'+esc(spec.title)+'</h1>'+rendered.images.map((f,i)=>`<figure><img src="${esc(path.basename(f))}" alt="${esc(scene.slides[i].title)}"><figcaption>${i+1}. ${esc(scene.slides[i].title)}</figcaption></figure>`).join('')+'</html>';
    fs.writeFileSync(path.join(out,'previews/index.html'),html);
    bundle(spec,path.dirname(source),out,converted.engine);
    if(scene.slides.some(s=>s.notes)) fs.writeFileSync(path.join(out,'notes.md'),scene.slides.map((s,i)=>`## ${i+1}. ${s.title}\n\n${s.notes||'(Sem notas)'}\n`).join('\n'));
    json(path.join(out,'visual-review.json'),{status:'pending',pages:[],issues:[],reviewer:'',method:'Inspect every rendered PNG, then record review with the review command.'});
    qa=await validateOutput(out);
    if(qa.status==='failed') throw new Error(`Verificação dos arquivos reprovada: ${qa.issues.length} problemas; veja ${out}/qa.json`);
    return {out,pptx,pdf:converted.pdf,slides:scene.slides.length,backend,status:qa.status};
  } catch(error) {
    const current=read(path.join(out,'qa.json')); current.status='failed'; current.error=error.message;
    json(path.join(out,'qa.json'),current); throw error;
  }
}
export async function main(args=process.argv.slice(2)) {
  const {command,opts}=parse(args);
  if(command==='doctor') return {...await python('doctor'),node:process.version,pptxgenjs:available(),preferredBackend:available()?'pptxgenjs':'ooxml'};
  if(command==='profiles') return Object.values(profiles).map(p=>p.name);
  if(command==='build') return build(opts);
  if(command==='extract') {
    if(!opts.input || !opts.out) throw new Error('--input e --out obrigatórios');
    return python('extract',{input:opts.input,out:opts.out});
  }
  if(command==='prepare') {
    if(!opts.prompt || !opts.out) throw new Error('--prompt e --out obrigatórios');
    const out=path.resolve(opts.out); if(fs.existsSync(out)) throw new Error('prepare exige uma pasta nova');
    fs.mkdirSync(out,{recursive:true});
    const source=opts.input?await python('extract',{input:opts.input,out:path.join(out,'sources')}):null;
    const request={prompt:opts.prompt,source,defaults:{slideCount:12,minutes:15,audience:'universitário',depth:'intermediária',language:'pt-BR',profile:profileKey(opts.theme||opts.profile)},next:'Codex: read SKILL.md, analyze sources, write deck.json, execute build and visually review every preview.'};
    json(path.join(out,'request.json'),request); return {out,...request};
  }
  if(!opts.out) throw new Error('--out obrigatório');
  if(command==='review') {
    if(!opts.file) throw new Error('--file obrigatório');
    const review=read(opts.file), scene=read(path.join(opts.out,'scene.json'));
    if(!['passed','failed','unavailable'].includes(review.status) || !Array.isArray(review.pages) || !Array.isArray(review.issues) || !review.method || !review.reviewer) throw new Error('Review exige status, pages, issues, method e reviewer');
    if(review.status==='passed' && (review.issues.length || review.pages.length!==scene.slides.length || !scene.slides.every((_,i)=>review.pages.includes(i+1)))) throw new Error('Review passed exige todas as páginas sem problemas abertos');
    json(path.join(opts.out,'visual-review.json'),{...review,fingerprint:fingerprint(opts.out),reviewedAt:new Date().toISOString()});
  }
  const qa=await validateOutput(opts.out); if(qa.status==='failed') process.exitCode=1; return qa;
}
if(process.argv[1] && fs.existsSync(process.argv[1]) && import.meta.url===pathToFileURL(fs.realpathSync(process.argv[1])).href) {
  main().then(value=>console.log(JSON.stringify(value,null,2))).catch(error=>{console.error(error.message);process.exitCode=1;});
}
