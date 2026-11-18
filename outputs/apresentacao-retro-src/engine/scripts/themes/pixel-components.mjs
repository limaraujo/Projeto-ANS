import fs from 'node:fs';
import path from 'node:path';
import {SIZE,textWidth} from '../model.mjs';

// Components return ordinary scene primitives. No React, CSS engine, rasterized slide or new backend.
function wrap(value,width,size,preserve=false) {
  if(preserve) return value;
  return value.split('\n').flatMap(p=>{
    const lines=[];let line='';
    for(const word of p.split(/\s+/)) {
      const next=line?`${line} ${word}`:word;
      if(line&&textWidth(next,size,true)>width*.96) {lines.push(line);line=word;} else line=next;
    }
    lines.push(line);return lines;
  }).join('\n');
}
export function pixelContext(theme,fonts,baseDir) {
  const elements=[];
  const c={theme,fonts,baseDir,elements};
  c.rect=(x,y,w,h,fill,component,part,role='panel')=>{
    const e={kind:'shape',shape:'rect',x,y,w,h,fill,role,component,part};elements.push(e);return e;
  };
  c.text=(value,x,y,w,h,fontSize=22,opts={})=>{
    const e={kind:'text',x,y,w,h,fontSize,font:fonts.body,color:theme.colors.foreground,mono:true,
      text:wrap(value,w,fontSize,opts.preserve),...opts};
    elements.push(e);return e;
  };
  c.image=(file,x,y,w,h,alt,component)=>{
    const resolved=path.resolve(baseDir,file);
    if(!fs.existsSync(resolved)||!/\.(svg|png|jpe?g)$/i.test(resolved)) throw new Error(`Imagem local inválida: ${file}`);
    elements.push({kind:'image',path:resolved,x,y,w,h,alt,role:'image',component});
  };
  return c;
}
function pixelFill(c,x,y,w,h,color,component,part) {
  const step=Math.min(4/72,w/5,h/5);
  c.rect(x+step,y,w-2*step,h,color,component,part);
  c.rect(x,y+step,w,h-2*step,color,component,part);
}
export function PixelCard(c,{x,y,w,h,highlight=false}) {
  const t=c.theme.effects.borderWidth/72, offset=c.theme.effects.shadowOffset/72, colors=c.theme.colors;
  c.rect(x+offset,y+offset,w,h,colors.shadow,'PixelCard','shadow');
  pixelFill(c,x,y,w,h,highlight?colors.accent:colors.border,'PixelCard','border');
  pixelFill(c,x+t,y+t,w-2*t,h-2*t,colors.surface,'PixelCard','surface');
  return {x:x+.28,y:y+.26,w:w-.56,h:h-.52};
}
export function PixelWindow(c,{x,y,w,h,title}) {
  const inner=PixelCard(c,{x,y,w,h});
  const t=c.theme.effects.borderWidth/72;
  c.rect(x+t,y+t,w-2*t,.5,c.theme.colors.border,'PixelWindow','title-bar');
  c.text(title,x+.2,y+.09,w-1.25,.36,18,{font:c.fonts.heading,color:c.theme.colors.background,
    background:c.theme.colors.border,role:'label',component:'PixelWindow',bold:true});
  for(let i=0;i<3;i++) c.rect(x+w-.8+i*.2,y+.19,.09,.09,c.theme.colors.background,'PixelWindow','control','decoration');
  return {...inner,y:y+.76,h:h-1.02};
}
export function PixelBadge(c,{x,y,text,highlight=false}) {
  const w=textWidth(text,18,true)+.32,h=.46;
  c.rect(x,y,w,h,highlight?c.theme.colors.accent:c.theme.colors.border,'PixelBadge','border');
  if(!highlight) c.rect(x+.02,y+.02,w-.04,h-.04,c.theme.colors.surface,'PixelBadge','surface');
  c.text(text,x+.16,y+.065,w-.32,.33,18,{role:'label',bold:true,component:'PixelBadge',
    font:c.fonts.heading,color:highlight?c.theme.colors.background:c.theme.colors.foreground,
    background:highlight?c.theme.colors.accent:c.theme.colors.surface,preserve:true});
  return w;
}
export function PixelDivider(c,{x=.65,y=1.92,w=12,highlight=false}={}) {
  const color=highlight?c.theme.colors.accent:c.theme.colors.border;
  c.rect(x,y,w,.025,color,'PixelDivider','line','decoration');
  for(let i=0;i<3;i++) c.rect(x+i*.13,y-.035,.07,.095,color,'PixelDivider','pixel','decoration');
}
export function PixelGridBackground(c,options={}) {
  const config={...c.theme.grid,...options};
  if(!config.enabled) return;
  const blend=(a,b,t)=>[0,2,4].map(i=>Math.round(parseInt(a.slice(i,i+2),16)*(1-t)+parseInt(b.slice(i,i+2),16)*t).toString(16).padStart(2,'0')).join('').toUpperCase();
  const fill=blend(c.theme.colors.background,config.color,config.opacity);
  for(let x=config.spacing;x<SIZE.w-.01;x+=config.spacing) c.rect(x,0,.006,SIZE.h,fill,'PixelGridBackground','vertical','decoration');
  for(let y=config.spacing;y<SIZE.h-.01;y+=config.spacing) c.rect(0,y,SIZE.w,.006,fill,'PixelGridBackground','horizontal','decoration');
}
const keywords=new Set(['def','return','if','else','elif','for','while','const','let','function','class','import','from','in','True','False','None','await','async','se','então','enquanto']);
export function syntaxTokens(line) {
  return [...line.matchAll(/#[^\n]*|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[\p{L}_][\p{L}\p{N}_]*|\d+(?:\.\d+)?|\s+|[^\s]/gu)].map(([text])=>({text,kind:/^(#|\/\/)/.test(text)?'comment':keywords.has(text)?'keyword':'plain'}));
}
export function PixelCodeBlock(c,{x,y,w,h,code,title='CÓDIGO',lineNumbers=false}) {
  const area=PixelWindow(c,{x,y,w,h,title}), lines=code.split('\n');
  const row=.4, size=20, gutter=lineNumbers?.62:0;
  if(lines.length*row>area.h+.05) throw new Error('PixelCodeBlock: código muito alto; divida em mais slides sem reduzir a fonte.');
  lines.forEach((line,i)=>{
    const yy=area.y+i*row;
    if(lineNumbers) c.text(String(i+1).padStart(2,'0'),area.x,yy,.42,.35,18,{role:'label',color:c.theme.readableMuted,background:c.theme.colors.surface,component:'PixelCodeBlock'});
    let xx=area.x+gutter;
    for(const token of syntaxTokens(line)) {
      const width=textWidth(token.text,size,true);
      if(token.text.trim()) c.text(token.text,xx,yy,width+.002,.36,size,{preserve:true,background:c.theme.colors.surface,
        color:token.kind==='keyword'?c.theme.colors.accent:token.kind==='comment'?c.theme.readableMuted:c.theme.colors.foreground,
        component:'PixelCodeBlock',syntax:token.kind});
      xx+=width;
    }
    if(xx>area.x+area.w+.005) throw new Error(`PixelCodeBlock: linha ${i+1} muito larga; quebre a linha no código.`);
  });
}
export function PixelDiagram(c,{x,y,w,h,steps,mainFlow=[0]}) {
  const gap=.43,n=steps.length,nw=(w-gap*(n-1))/n;
  steps.forEach((text,i)=>{
    const xx=x+i*(nw+gap), area=PixelCard(c,{x:xx,y,w:nw,h});
    c.text(String(i+1).padStart(2,'0'),area.x,area.y,nw-.56,.4,20,{background:c.theme.colors.surface,color:i===0?c.theme.colors.accent:c.theme.colors.foreground,component:'PixelDiagram',bold:true});
    c.text(text,area.x,area.y+.65,area.w,h-1.1,20,{background:c.theme.colors.surface,component:'PixelDiagram'});
    if(i<n-1) {
      const color=mainFlow.includes(i)?c.theme.colors.accent:c.theme.colors.border, start=xx+nw+.07,mid=y+h/2;
      c.rect(start,mid-.0125,.2,.025,color,'PixelDiagram','connector','connector');
      for(let j=0;j<3;j++) c.rect(start+.16+j*.04,mid-(.1-j*.03),.04,.2-j*.06,color,'PixelDiagram','arrow','connector');
    }
  });
}
export function PixelDuck(c,{x,y,w=1.5,h=1.3,path:file}={}) {
  if(file) {c.image(file,x,y,w,h,'Mascote pixelado fornecido pelo usuário','PixelDuck');return;}
  // Discreet original placeholder made from editable squares; no third-party mascot assumed.
  const mask=['00001110','00001011','00001110','00111100','01111100','00111000','00011000'];
  const pixel=Math.min(w/8,h/7);
  mask.forEach((row,j)=>[...row].forEach((v,i)=>{
    if(v==='1') c.rect(x+i*pixel,y+j*pixel,pixel,pixel,c.theme.colors.foreground,'PixelDuck','placeholder','decoration');
  }));
}
