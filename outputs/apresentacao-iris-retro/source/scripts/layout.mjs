import fs from 'node:fs';
import path from 'node:path';
import { profiles, profileKey, SIZE, wrapText, validateSpec } from './model.mjs';
import {compileRetro} from './themes/retroui-pixel.mjs';

export function compile(spec, baseDir = process.cwd(), profileOverride) {
  validateSpec(spec,profileOverride);
  const key = profileKey(profileOverride || spec.plan.profile);
  const p = profiles[key];
  if(key==='retroui-pixel') return compileRetro(spec,baseDir);
  const scene = { ...SIZE, profile: key, title: spec.title, language: spec.plan.language, slides: [] };
  for (const [index,s] of spec.slides.entries()) {
    const elements=[];
    const box=(kind,x,y,w,h,opts={})=>{ const e={kind,x,y,w,h,...opts}; elements.push(e); return e; };
    const text=(value,x,y,w,h,size=24,opts={}) => box('text',x,y,w,h,{text:wrapText(value,w,size,opts.mono),fontSize:size,font:p.font,color:p.foreground,...opts});
    const panel=(x,y,w,h)=>box('shape',x,y,w,h,{shape:'rect',fill:p.panel,role:'panel'});
    box('shape',.55,.5,.12,.55,{shape:'rect',fill:p.accent,role:'decoration'});
    if (s.layout !== 'title') text(s.title,.85,.46,11.7,.95,32,{bold:true,role:'title'});
    const foot = `${String(index+1).padStart(2,'0')} / ${spec.slides.length}  ·  ${s.citations?.map(id=>`[${id}]`).join(' ') || p.name}`;
    text(foot,.65,7.13,11.95,.24,12,{color:p.muted,role:'footer'});
    if (s.label) text(s.label,.85,1.43,11.6,.38,18,{color:p.accent,role:'label',bold:true});
    const bullets=(items,x,y,w,h,size=24,background=p.background)=>{
      const gap=.22;
      const each=(h-gap*(items.length-1))/items.length;
      items.forEach((v,i)=>{
        box('shape',x,y+i*(each+gap)+.11,.07,.07,{shape:'ellipse',fill:p.accent,role:'decoration'});
        text(v,x+.22,y+i*(each+gap),w-.22,each,size,{background});
      });
    };
    switch(s.layout) {
      case 'title':
        text(s.title,.85,1.7,11.5,2.0,44,{bold:true,role:'title'});
        text(s.subtitle,.9,4.05,10.8,1.25,26,{color:p.muted});
        text(`${spec.plan.audience}  ·  ${spec.plan.minutes} min`,.9,6.05,11.4,.5,20,{color:p.accent});
        break;
      case 'bullets': bullets(s.bullets,.9,2,11.5,4.5); break;
      case 'columns':
        s.columns.forEach((c,j)=>{
          const x=.8+j*6.1; panel(x,1.95,5.7,4.75);
          text(c.title,x+.28,2.2,5.12,.8,25,{bold:true,color:p.accent,background:p.panel});
          bullets(c.bullets,x+.28,3.25,5.12,3.05,22,p.panel);
        }); break;
      case 'process': {
        const w=(11.7-(s.steps.length-1)*.45)/s.steps.length;
        s.steps.forEach((step,j)=>{
          const x=.8+j*(w+.45); panel(x,2.3,w,2.4);
          text(String(j+1).padStart(2,'0'),x+.2,2.53,w-.4,.5,24,{color:p.accent,bold:true,background:p.panel});
          text(step,x+.2,3.22,w-.4,1.22,22,{background:p.panel});
          if(j<s.steps.length-1) box('shape',x+w+.1,3.4,.25,.25,{shape:'chevron',fill:p.accent,role:'connector'});
        });
        text(s.takeaway,1,5.4,11.1,.95,25,{bold:true}); break;
      }
      case 'equation':
        panel(.85,2.05,11.6,1.4);
        text(s.equation,1.1,2.4,11.1,.8,28,{color:p.accent,bold:true,background:p.panel});
        bullets(s.bullets,1,3.95,11.1,2.7,22); break;
      case 'code':
        panel(.85,1.95,11.6,3.85);
        text(s.code,1.1,2.18,11.1,3.4,20,{font:p.mono,mono:true,background:p.panel});
        text(s.caption,1,6.05,11.1,.7,20,{color:p.muted}); break;
      case 'scatter': {
        const area={x:1.2,y:2,w:7.5,h:3.9};
        panel(.9,1.85,8.15,4.75);
        const xs=s.points.map(q=>q.x), ys=s.points.map(q=>q.y);
        const loX=Math.min(...xs), loY=Math.min(...ys), dx=Math.max(...xs)-loX||1, dy=Math.max(...ys)-loY||1;
        const groups=[...new Set(s.points.map(q=>q.group))];
        const colors=[p.accent,p.secondary,p.muted];
        for(const q of s.points) box('shape',area.x+.2+(q.x-loX)/dx*(area.w-.4),area.y+.2+(1-(q.y-loY)/dy)*(area.h-.4),.11,.11,{shape:'ellipse',fill:colors[groups.indexOf(q.group)%3],role:'data'});
        text(s.xLabel,1.2,6.13,7.5,.35,18,{color:p.muted,role:'label',background:p.panel});
        text(s.yLabel,9.5,2,2.7,.65,18,{role:'label',color:p.muted});
        groups.forEach((g,j)=>text(g,9.5,3+j*.7,2.65,.55,20,{color:colors[j%3],bold:true}));
        text(s.caption,1,6.75,11.2,.35,18,{role:'label'}); break;
      }
      case 'bar': {
        const chart=box('chart',1,2,11.25,3.8,{labels:s.labels,values:s.values,unit:s.unit,colors:[p.accent,p.secondary],color:p.foreground,background:p.background,font:p.font,role:'chart'});
        text(s.caption,1,6.05,11.1,.85,20,{color:p.muted});
        // These primitives are the editable fallback for engines without chart support.
        chart.fallback=[];
        const original=elements.length;
        const row=3.6/s.labels.length, max=Math.max(...s.values);
        s.labels.forEach((label,j)=>{
          const y=2+j*row;
          text(label,1,y,3,.5,18,{role:'label'});
          if(s.values[j]>0) box('shape',4.2,y+.05,6.1*s.values[j]/max,.3,{shape:'rect',fill:p.accent,role:'data'});
          text(String(s.values[j]),10.6,y,1.45,.45,18,{role:'label'});
        });
        text(s.unit,4.2,5.7,6.1,.35,18,{role:'label',color:p.muted});
        chart.fallback=elements.splice(original);
        break;
      }
      case 'figure': {
        const imagePath=path.resolve(baseDir,s.path);
        if(!fs.existsSync(imagePath)) throw new Error(`Imagem inexistente: ${imagePath}`);
        if(!/\.(png|jpe?g|svg)$/i.test(imagePath)) throw new Error('Imagem: use PNG, JPG ou SVG');
        box('image',1.0,2,11.1,3.7,{path:imagePath,alt:s.alt,role:'image'});
        text(s.caption,1,5.95,11.1,.7,20);
        text(s.attribution,1,6.76,11.1,.25,12,{role:'footer',color:p.muted}); break;
      }
      case 'references':
        s.ids.forEach((id,j)=>{
          const r=spec.references.find(r=>r.id===id), y=2+j*1.5;
          text(`[${id}] ${r.text}`,1,y,11.15,.8,18,{role:'label'});
          text(r.url,1,y+.85,11.15,.4,14,{role:'reference',color:p.accent,url:r.url.startsWith('http')?r.url:undefined});
        }); break;
    }
    scene.slides.push({background:p.background,elements,notes:s.notes || '',title:s.title});
  }
  return scene;
}
