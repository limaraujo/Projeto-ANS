import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {ROOT,profiles,validateSpec,checkLayout,contrast} from '../scripts/model.mjs';
import {compile} from '../scripts/layout.mjs';
const fixture=path.join(ROOT,'tests/fixtures/dbscan.json');
const spec=()=>JSON.parse(fs.readFileSync(fixture));
const make=()=>compile(spec(),path.dirname(fixture));
test('12 slides e os três perfis mantêm os mínimos de legibilidade',()=>{
  for(const key of Object.keys(profiles)) {
    const s=compile(spec(),path.dirname(fixture),key);
    assert.equal(s.slides.length,12); assert.deepEqual(checkLayout(s),[]);
    assert.ok(contrast(profiles[key].foreground,profiles[key].background)>=4.5);
  }
});
test('citações inexistentes, bibliografia ausente e contagem incorreta são recusadas',()=>{
  let s=spec(); s.slides[1].citations=['inexistente']; assert.throws(()=>validateSpec(s),/citação/);
  s=spec(); s.slides[11].ids=['SK']; assert.throws(()=>validateSpec(s),/bibliografia/);
  s=spec(); s.plan.slideCount=11; assert.throws(()=>validateSpec(s),/slideCount/);
});
test('limites, sobreposição, fonte, contraste e cortes estimados são detectados',()=>{
  const scene=make(), s=scene.slides[1], e=s.elements.find(e=>e.kind==='text'&&e.role!=='title'&&e.role!=='footer');
  e.x=-1; e.fontSize=8; e.color=s.background; e.text='conteúdo '.repeat(1000);
  s.elements.push({...e,x:1,y:2,w:3,h:2});
  s.elements.push({...e,x:1,y:2,w:3,h:2});
  const codes=new Set(checkLayout(scene).map(i=>i.code));
  for(const code of ['bounds','font','contrast','text-overflow','overlap']) assert.ok(codes.has(code),code);
});
test('valores e figuras inválidos são recusados antes da geração',()=>{
  let s=spec(); s.slides[7].values[0]=-1; assert.throws(()=>validateSpec(s),/valores/);
  s=spec(); s.slides[9].path='missing.svg'; assert.throws(()=>compile(s,path.dirname(fixture)),/inexistente/);
});
test('dados sintéticos declarados correspondem às contagens mostradas',()=>{
  const s=spec(), pts=s.slides[6].points, indices=[0,6,12];
  const counts=indices.map(i=>pts.filter(q=>Math.hypot(q.x-pts[i].x,q.y-pts[i].y)<=.5).length);
  assert.deepEqual(counts,s.slides[7].values);
  assert.equal(pts.length,15);
});
