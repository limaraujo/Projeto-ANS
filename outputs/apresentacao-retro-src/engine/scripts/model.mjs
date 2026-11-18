import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
export const profiles = JSON.parse(fs.readFileSync(path.join(ROOT, 'assets/templates/profiles.json'), 'utf8'));
export const SIZE = { w: 13.333333, h: 7.5 };
const layouts = new Set(['title','bullets','columns','process','equation','code','scatter','bar','figure','references']);
export const retroLayouts = Object.freeze({CoverSlide:'title',SectionSlide:'section',ContentSlide:'bullets',TwoColumnSlide:'columns',CodeSlide:'code',DiagramSlide:'process',ComparisonSlide:'columns',ResultsSlide:'bar',ConclusionSlide:'bullets',ReferencesSlide:'references'});
export const canonicalLayout = (name, profile) => profile==='retroui-pixel' ? (retroLayouts[name] || name) : name;
const need = (ok, message) => { if (!ok) throw new Error(message); };
const str = v => typeof v === 'string' && v.trim().length > 0;
const strings = v => Array.isArray(v) && v.length > 0 && v.every(str);
export function profileKey(value = 'academic-minimal') {
  const key = value.toLowerCase().replaceAll(' ', '-');
  need(profiles[key], `Perfil desconhecido: ${value}`); return key;
}
export function validateSpec(spec, profileOverride) {
  need(str(spec.title), 'title obrigatório');
  const p = spec.plan;
  need(p && typeof p === 'object', 'plan obrigatório');
  for (const k of ['objective','audience','depth','language','narrative']) need(str(p[k]), `plan.${k} obrigatório`);
  need(Number.isFinite(p.minutes) && p.minutes > 0, 'plan.minutes deve ser positivo');
  need(Array.isArray(p.assumptions) && p.assumptions.every(str), 'plan.assumptions deve ser array de textos');
  need(p.analysis && str(p.analysis.centralTheme), 'plan.analysis.centralTheme obrigatório');
  for (const k of ['concepts','arguments','results','visualOpportunities']) need(Array.isArray(p.analysis[k]) && p.analysis[k].every(str), `plan.analysis.${k} deve ser array de textos`);
  const profile=profileKey(profileOverride || p.profile);
  if(profile==='retroui-pixel' && spec.visual) {
    const v=spec.visual;
    need(!('grid' in v) || typeof v.grid==='boolean', 'visual.grid deve ser booleano');
    need(!('gridOpacity' in v) || (Number.isFinite(v.gridOpacity)&&v.gridOpacity>=0&&v.gridOpacity<=1), 'visual.gridOpacity: 0–1');
    need(!('gridSpacing' in v) || (Number.isFinite(v.gridSpacing)&&v.gridSpacing>=.25&&v.gridSpacing<=2), 'visual.gridSpacing: 0,25–2 polegadas');
    need(!('duckPath' in v) || str(v.duckPath), 'visual.duckPath deve ser caminho local');
    need(!('lineNumbers' in v) || typeof v.lineNumbers==='boolean', 'visual.lineNumbers deve ser booleano');
  }
  need(Array.isArray(spec.slides) && spec.slides.length > 0 && spec.slides.length <= 200, 'slides: entre 1 e 200');
  need(Number.isInteger(p.slideCount) && p.slideCount === spec.slides.length, 'plan.slideCount difere do número de slides');
  need(Array.isArray(spec.references), 'references deve ser array');
  const refs = new Set();
  for (const r of spec.references) {
    need(str(r.id) && !refs.has(r.id) && str(r.text) && str(r.url), 'Referência sem id/text/url ou id duplicado');
    need(/^https?:\/\//.test(r.url) || /^file:/.test(r.url), `Origem inválida: ${r.url}`);
    refs.add(r.id);
  }
  spec.slides.forEach((s, i) => {
    const at = `Slide ${i + 1}`;
    s={...s,layout:canonicalLayout(s.layout,profile)};
    need((layouts.has(s.layout)||(profile==='retroui-pixel'&&s.layout==='section')) && str(s.title), `${at}: layout ou título inválido`);
    if(profile==='retroui-pixel') {
      if(s.layout==='section') need(str(s.subtitle),`${at}: subtitle obrigatório`);
      need(!s.badges || (strings(s.badges)&&s.badges.length<=3&&s.badges.every(v=>v.length<=24)),`${at}: use até 3 badges curtos (24 caracteres)`);
      need(!('grid' in s)||typeof s.grid==='boolean',`${at}: grid deve ser booleano`);
      need(!('lineNumbers' in s)||typeof s.lineNumbers==='boolean',`${at}: lineNumbers deve ser booleano`);
      need(!('duck' in s)||typeof s.duck==='boolean',`${at}: duck deve ser booleano`);
      need(!s.duckPath||str(s.duckPath),`${at}: duckPath inválido`);
      need(!s.mainFlow||(Array.isArray(s.mainFlow)&&s.mainFlow.every(n=>Number.isInteger(n)&&n>=0&&n<(s.steps?.length||0)-1)),`${at}: mainFlow inválido`);
      need(!('highlightIndex' in s)||(Number.isInteger(s.highlightIndex)&&s.highlightIndex>=0&&s.highlightIndex<(s.values?.length||0)),`${at}: highlightIndex inválido`);
    }
    need(!s.notes || str(s.notes), `${at}: notes deve ser texto`);
    need(!s.citations || (Array.isArray(s.citations) && s.citations.every(id => refs.has(id))), `${at}: citação desconhecida`);
    if (s.layout === 'title') need(str(s.subtitle), `${at}: subtitle obrigatório`);
    if (s.layout === 'bullets') need(strings(s.bullets) && s.bullets.length <= 6, `${at}: use 1–6 bullets`);
    if (s.layout === 'columns') {
      need(Array.isArray(s.columns) && s.columns.length === 2, `${at}: exatamente duas colunas`);
      for (const c of s.columns) need(str(c.title) && strings(c.bullets) && c.bullets.length <= 5, `${at}: coluna inválida`);
    }
    if (s.layout === 'process') need(strings(s.steps) && s.steps.length >= 2 && s.steps.length <= 4 && str(s.takeaway), `${at}: 2–4 steps e takeaway`);
    if (s.layout === 'equation') need(str(s.equation) && strings(s.bullets) && s.bullets.length <= 4, `${at}: equation e bullets obrigatórios`);
    if (s.layout === 'code') need(str(s.code) && str(s.caption), `${at}: code e caption obrigatórios`);
    if (s.layout === 'scatter') {
      need(Array.isArray(s.points) && s.points.length >= 1 && s.points.length <= 500, `${at}: 1–500 points`);
      for (const pt of s.points) need(Number.isFinite(pt.x) && Number.isFinite(pt.y) && str(pt.group), `${at}: ponto inválido`);
      need(str(s.caption) && str(s.xLabel) && str(s.yLabel), `${at}: caption, xLabel e yLabel obrigatórios`);
    }
    if (s.layout === 'bar') {
      need(strings(s.labels) && Array.isArray(s.values) && s.values.length === s.labels.length && s.values.length <= 8, `${at}: labels/values inválidos`);
      need(s.values.every(v => Number.isFinite(v) && v >= 0) && Math.max(...s.values) > 0, `${at}: valores devem ser finitos, não negativos e algum positivo`);
      need(str(s.caption) && str(s.unit), `${at}: caption e unit obrigatórios`);
    }
    if (s.layout === 'figure') need(str(s.path) && str(s.caption) && str(s.attribution) && str(s.alt), `${at}: path/caption/attribution/alt obrigatórios`);
    if (s.layout === 'references') need(strings(s.ids) && s.ids.length <= 3 && s.ids.every(id => refs.has(id)), `${at}: 1–3 referências existentes`);
  });
  const cited = new Set(spec.slides.flatMap(s => s.citations || []));
  const listed = new Set(spec.slides.filter(s => canonicalLayout(s.layout,profile) === 'references').flatMap(s => s.ids));
  for (const id of cited) need(listed.has(id), `Referência citada ${id} ausente na bibliografia`);
  return spec;
}
export function textWidth(text, fontSize, mono = false) {
  let em = 0;
  for (const ch of text) {
    if (mono) em += 0.62;
    else if (/[ilI.,:;!|' ]/.test(ch)) em += 0.31;
    else if (/[MW@%]/.test(ch)) em += 0.9;
    else if (ch.codePointAt(0) > 0x2fff) em += 1;
    else em += 0.58;
  }
  return em * fontSize / 72;
}
export function wrapText(text, width, fontSize, mono = false) {
  const lines = [];
  for (const paragraph of text.split('\n')) {
    if (!paragraph) { lines.push(''); continue; }
    if (mono) { lines.push(paragraph); continue; }
    let line = '';
    for (const word of paragraph.split(/\s+/)) {
      const next = line ? `${line} ${word}` : word;
      if (line && textWidth(next, fontSize) > width * 0.94) { lines.push(line); line = word; }
      else line = next;
    }
    lines.push(line);
  }
  return lines.join('\n');
}
export function contrast(a, b) {
  const lum = hex => {
    const rgb = hex.match(/../g).map(h => parseInt(h,16)/255).map(x => x <= .04045 ? x/12.92 : ((x+.055)/1.055)**2.4);
    return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2];
  };
  const [x,y] = [lum(a),lum(b)].sort((a,b)=>b-a); return (x+.05)/(y+.05);
}
export function checkLayout(scene) {
  const issues = [];
  for (const [si,s] of scene.slides.entries()) {
    const report = (code, element, message) => issues.push({ slide: si+1, code, element, message });
    const elements=s.elements.flatMap(e=>e.kind==='chart'?[e,...e.fallback]:[e]);
    for (const [ei,e] of elements.entries()) {
      if (![e.x,e.y,e.w,e.h].every(Number.isFinite) || e.w <= 0 || e.h <= 0 || e.x < -.001 || e.y < -.001 || e.x+e.w > SIZE.w+.001 || e.y+e.h > SIZE.h+.001) report('bounds',ei,'Elemento fora dos limites ou dimensão inválida');
      if (e.kind === 'text') {
        const min = e.role === 'footer' ? 12 : e.role === 'reference' ? 14 : e.role === 'label' ? 18 : e.role === 'title' ? 30 : 20;
        if (e.fontSize < min) report('font',ei,`Fonte abaixo de ${min} pt`);
        const lines = e.text.split('\n');
        if (lines.length * e.fontSize * 1.23 / 72 > e.h + .025 || lines.some(l => textWidth(l,e.fontSize,e.mono) > e.w)) report('text-overflow',ei,'Estimativa de texto excede caixa; reescreva, amplie a caixa ou divida o slide');
        if (contrast(e.color,e.background || s.background) < 4.5) report('contrast',ei,'Contraste de texto menor que 4,5:1');
      }
    }
    const items = elements.map((e,i)=>({...e,i})).filter(e => !['panel','decoration','data','connector','chart'].includes(e.role));
    for (let a=0; a<items.length; a++) for (let b=a+1; b<items.length; b++) {
      const x=items[a], y=items[b];
      if (Math.min(x.x+x.w,y.x+y.w)-Math.max(x.x,y.x) > .035 && Math.min(x.y+x.h,y.y+y.h)-Math.max(x.y,y.y) > .035) report('overlap',`${x.i},${y.i}`,'Caixas de conteúdo se sobrepõem');
    }
  }
  return issues;
}
