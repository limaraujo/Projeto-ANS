import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {ROOT,profiles,canonicalLayout,checkLayout,validateSpec} from '../scripts/model.mjs';
import {compile} from '../scripts/layout.mjs';
import {resolveFonts} from '../scripts/fonts.mjs';
import {compileRetro} from '../scripts/themes/retroui-pixel.mjs';
import * as components from '../scripts/themes/pixel-components.mjs';
import {build,main,python} from '../scripts/cli.mjs';
import {updateRetro} from '../scripts/update-retro.mjs';
const fixture=path.join(ROOT,'tests/fixtures/retroui-pixel.json');
const spec=()=>JSON.parse(fs.readFileSync(fixture));
const compileDemo=()=>compile(spec(),path.dirname(fixture));

test('os três perfis anteriores preservam exatamente suas cenas',()=>{
  const baseline=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/fixtures/classic-layout-hashes.json')));
  const deck=JSON.parse(fs.readFileSync(path.join(ROOT,'tests/fixtures/dbscan.json')));
  for(const [profile,expected] of Object.entries(baseline)) {
    const scene=compile(deck,path.dirname(fixture),profile);
    for(const s of scene.slides) for(const e of s.elements) if(e.path)e.path=path.basename(e.path);
    assert.equal(crypto.createHash('sha256').update(JSON.stringify(scene)).digest('hex'),expected);
  }
});
test('dez layouts, oito componentes e tokens retro são integrados sem rasterizar slides',()=>{
  const deck=spec(),scene=compileDemo(),items=scene.slides.flatMap(s=>s.elements);
  assert.deepEqual(checkLayout(scene),[]);
  for(const name of ['CoverSlide','SectionSlide','ContentSlide','TwoColumnSlide','CodeSlide','DiagramSlide','ComparisonSlide','ResultsSlide','ConclusionSlide','ReferencesSlide']) assert.ok(deck.slides.some(s=>s.layout===name),name);
  for(const name of ['PixelCard','PixelWindow','PixelBadge','PixelDivider','PixelCodeBlock','PixelDiagram','PixelGridBackground','PixelDuck']) {
    assert.equal(typeof components[name],'function');assert.ok(items.some(e=>e.component===name),name);
  }
  assert.equal(profiles['retroui-pixel'].colors.accent,'FFD400');
  assert.equal(profiles['retroui-pixel'].muted,'777777');
  assert.equal(items.filter(e=>e.kind==='image').length,0);
  for(const s of scene.slides) assert.ok(s.elements.some(e=>e.kind==='text'));
  const shadow=items.find(e=>e.part==='shadow'),edge=items.find(e=>e.part==='border'&&e.component==='PixelCard');
  const side=items.find(e=>e.part==='border'&&e.component==='PixelCard'&&e.y>edge.y);
  assert.equal(shadow.fill,'000000');assert.ok(Math.abs(shadow.x-side.x-4/72)<.00001);
  assert.ok(Math.abs(shadow.y-edge.y-4/72)<.00001);
});
test('grade e numeração são configuráveis; palavras-chave mantêm cor própria',()=>{
  let deck=spec();deck.visual.grid=false;
  let scene=compile(deck,path.dirname(fixture));assert.ok(!scene.slides.flatMap(s=>s.elements).some(e=>e.component==='PixelGridBackground'));
  deck=spec();deck.slides[4].lineNumbers=false;
  scene=compile(deck,path.dirname(fixture));
  const code=scene.slides[4].elements.filter(e=>e.component==='PixelCodeBlock');
  assert.ok(code.some(e=>e.text==='return'&&e.color==='FFD400'));
  assert.ok(code.some(e=>e.syntax==='comment'&&e.color==='AAAAAA'));
  assert.ok(!code.some(e=>e.role==='label'));
  deck=spec();deck.visual.gridSpacing=.01;assert.throws(()=>validateSpec(deck),/gridSpacing/);
});
test('fontes reais são verificadas e fallbacks são explícitos',()=>{
  const p=profiles['retroui-pixel'];
  const all=resolveFonts(p,()=>true);assert.equal(all.resolved.heading,'Pixelify Sans');
  const fallback=resolveFonts(p,f=>f==='Liberation Mono');
  assert.equal(fallback.resolved.body,'Liberation Mono');assert.equal(fallback.warnings.length,3);
  assert.throws(()=>resolveFonts(p,()=>false),/indisponível/);
  const scene=compileRetro(spec(),path.dirname(fixture),f=>f==='Liberation Mono');assert.deepEqual(checkLayout(scene),[]);
});
test('limites do código, aliases e dados inválidos são recusados',()=>{
  let deck=spec();deck.slides[4].code='x'.repeat(120);assert.throws(()=>compile(deck,path.dirname(fixture)),/muito larga/);
  deck=spec();deck.slides[4].code=Array(20).fill('return x').join('\n');assert.throws(()=>compile(deck,path.dirname(fixture)),/muito alto/);
  deck=spec();deck.plan.profile='academic-minimal';assert.throws(()=>validateSpec(deck),/layout/);
  assert.equal(canonicalLayout('ComparisonSlide','retroui-pixel'),'columns');
  deck=spec();deck.slides[7].highlightIndex=10;assert.throws(()=>validateSpec(deck),/highlightIndex/);
});
test('atualização incremental preserva temas extras e recusa conflitos antes de escrever',t=>{
  const temp=fs.mkdtempSync(path.join(os.tmpdir(),'retro-update-test-'));t.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
  const target=path.join(temp,'slides-creator');
  fs.cpSync(ROOT,target,{recursive:true,filter:src=>!['outputs','node_modules','__pycache__','.git'].includes(path.basename(src))});
  const profileFile=path.join(target,'assets/templates/profiles.json');
  const original=JSON.parse(fs.readFileSync(profileFile));delete original['retroui-pixel'];original['custom-team']={name:'Meu perfil'};
  fs.writeFileSync(profileFile,JSON.stringify(original));
  const dry=updateRetro(target,true);assert.deepEqual(dry.files,['assets/templates/profiles.json']);assert.ok(!JSON.parse(fs.readFileSync(profileFile))['retroui-pixel']);
  updateRetro(target);const after=JSON.parse(fs.readFileSync(profileFile));
  for(const [key,value] of Object.entries(original)) assert.deepEqual(after[key],value);
  assert.ok(after['retroui-pixel']);assert.ok(fs.existsSync(path.join(target,'.retroui-pixel-backup/assets/templates/profiles.json')));
  assert.equal(updateRetro(target).files.length,0);
  fs.appendFileSync(path.join(target,'scripts/layout.mjs'),'\n// modificação local\n');
  assert.throws(()=>updateRetro(target),/Alterações locais/);
  assert.deepEqual(JSON.parse(fs.readFileSync(profileFile)),after);
});
test('integração retro: 12 páginas, fontes, editabilidade, SVG/PNG e reprodução',{timeout:180000},async t=>{
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'slides-retro-'));t.after(()=>fs.rmSync(tmp,{recursive:true,force:true}));
  const out=path.join(tmp,'demo');
  await main(['build','--spec',fixture,'--out',out,'--theme','retroui-pixel','--backend','ooxml','--pdf-engine','native']);
  const qa=JSON.parse(fs.readFileSync(path.join(out,'qa.json')));
  assert.equal(qa.pdfPages,12);assert.equal(qa.previewCount,12);assert.deepEqual(qa.issues,[]);assert.ok(qa.fonts.resolved.body);
  const inspect=await python('integrity',{pptx:path.join(out,'presentation.pptx'),scene:path.join(out,'scene.json')});assert.deepEqual(inspect.issues,[]);
  await assert.rejects(main(['build','--spec',fixture,'--out',path.join(tmp,'invalid'),'--theme','retroui-pixel','--profile','Dark Technical']),/mesmo tema/);
  const listed=await main(['profiles']);
  for(const name of ['Academic Minimal','Dark Technical','Modern Scientific','retroui-pixel']) assert.ok(listed.includes(name));
  const request=await main(['prepare','--prompt','Crie 12 slides utilizando o tema retroui-pixel','--theme','retroui-pixel','--out',path.join(tmp,'request')]);assert.equal(request.defaults.profile,'retroui-pixel');
  const deck=spec();deck.slides=[deck.slides[0],deck.slides[9]];deck.plan.slideCount=2;
  deck.visual.duckPath=path.join(ROOT,'tests/fixtures/pixel-duck.svg');
  deck.slides[1].duckPath=path.join(ROOT,'tests/fixtures/pixel-duck.png');
  const input=path.join(tmp,'mascots.json');fs.writeFileSync(input,JSON.stringify(deck));
  const mascots=path.join(tmp,'mascots');await build({spec:input,out:mascots,backend:'ooxml','pdf-engine':'native'});
  const source=path.join(mascots,'source'),copied=JSON.parse(fs.readFileSync(path.join(source,'deck.json')));
  assert.ok(fs.existsSync(path.join(source,copied.visual.duckPath)));assert.ok(fs.existsSync(path.join(source,copied.slides[1].duckPath)));
  await build({spec:path.join(source,'deck.json'),out:path.join(tmp,'reproduced'),backend:'ooxml','pdf-engine':'native'});
});
