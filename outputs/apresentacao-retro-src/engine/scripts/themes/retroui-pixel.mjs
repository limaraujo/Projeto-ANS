import {profiles,SIZE,canonicalLayout} from '../model.mjs';
import {resolveFonts} from '../fonts.mjs';
import {pixelContext,PixelCard,PixelWindow,PixelBadge,PixelDivider,PixelCodeBlock,PixelDiagram,PixelGridBackground,PixelDuck} from './pixel-components.mjs';

export function compileRetro(spec,baseDir,fontProbe) {
  const theme=profiles['retroui-pixel'], fonts=resolveFonts(theme,fontProbe), visual=spec.visual||{};
  const scene={...SIZE,profile:'retroui-pixel',title:spec.title,language:spec.plan.language,fonts,slides:[]};
  spec.slides.forEach((s,index)=>{
    const c=pixelContext(theme,fonts.resolved,baseDir), colors=theme.colors;
    const layout=canonicalLayout(s.layout,'retroui-pixel');
    const head=(value,x,y,w,h,size=32,opts={})=>c.text(value,x,y,w,h,size,{font:fonts.resolved.heading,bold:true,role:'title',...opts});
    const text=(value,x,y,w,h,size=22,opts={})=>c.text(value,x,y,w,h,size,opts);
    const bullets=(items,area,size=22)=>{
      const gap=.18,each=(area.h-gap*(items.length-1))/items.length;
      items.forEach((v,j)=>{
        c.rect(area.x,area.y+j*(each+gap)+.1,.07,.07,colors.foreground,'ContentSlide','bullet','decoration');
        text(v,area.x+.22,area.y+j*(each+gap),area.w-.22,each,size,{background:colors.surface});
      });
    };
    PixelGridBackground(c,{enabled:s.grid??visual.grid??theme.grid.enabled,opacity:visual.gridOpacity??theme.grid.opacity,spacing:visual.gridSpacing??theme.grid.spacing});
    const foot=`${String(index+1).padStart(2,'0')} / ${spec.slides.length}  ${s.citations?.map(id=>`[${id}]`).join(' ')||'retroui-pixel'}`;
    text(foot,.65,7.13,12,.24,12,{role:'footer',color:theme.readableMuted});
    let top=2.18;
    if(layout!=='title'&&layout!=='section') {
      head(s.title,.65,.5,12,1.16);
      PixelDivider(c);
      if(s.label) {text(s.label,.8,2.08,11.6,.68,18,{role:'label',color:theme.readableMuted});top=2.94;}
      if(s.badges) {
        let x=.8;
        s.badges.forEach((label,i)=>{x+=PixelBadge(c,{x,y:top,text:label,highlight:i===0})+.2;});
        top+=.7;
      }
    }
    if(layout==='title') {
      PixelBadge(c,{x:.85,y:.65,text:'SEMINÁRIO',highlight:true});
      head(s.title,.85,1.7,11.4,2.1,40);
      text(s.subtitle,.9,4.05,10.9,1,24);
      text(`${spec.plan.audience} · ${spec.plan.minutes} min`,.9,5.65,8.4,.8,20,{color:theme.readableMuted});
      PixelDivider(c,{x:.85,y:6.68,w:11.6});
      if(s.duck!==false) PixelDuck(c,{x:10.35,y:5.2,w:1.5,h:1.2,path:s.duckPath||visual.duckPath});
    } else if(layout==='section') {
      PixelBadge(c,{x:.85,y:1.1,text:s.section||'PRÓXIMA SEÇÃO',highlight:true});
      head(s.title,.85,2.4,11.4,1.5,40);
      text(s.subtitle,.9,4.25,10.8,1.25,24);
      PixelDivider(c,{x:.85,y:6.2,w:11.6,highlight:true});
    } else if(layout==='bullets') {
      const showDuck=s.duck===true||!!s.duckPath;
      const area=PixelWindow(c,{x:.8,y:top,w:showDuck?8.7:11.7,h:6.72-top,title:s.windowTitle|| (s.layout==='ConclusionSlide'?'CONCLUSÕES':'CONCEITOS')});
      bullets(s.bullets,area);
      if(showDuck) PixelDuck(c,{x:10.25,y:top+.9,w:1.8,h:1.6,path:s.duckPath||visual.duckPath});
    } else if(layout==='columns') {
      s.columns.forEach((column,j)=>{
        const area=PixelWindow(c,{x:.8+j*6,y:top,w:5.65,h:6.72-top,title:column.title});
        bullets(column.bullets,area,20);
      });
    } else if(layout==='code') {
      PixelCodeBlock(c,{x:.8,y:top,w:11.7,h:6.1-top,code:s.code,title:s.codeTitle||'CÓDIGO',lineNumbers:s.lineNumbers??visual.lineNumbers??false});
      text(s.caption,.85,6.35,11.6,.72,20,{color:theme.readableMuted});
    } else if(layout==='process') {
      PixelDiagram(c,{x:.8,y:top+.15,w:11.7,h:2.5,steps:s.steps,mainFlow:s.mainFlow});
      text(s.takeaway,.85,top+3.1,11.55,6.75-(top+3.1),22,{bold:true});
    } else if(layout==='bar') {
      PixelCard(c,{x:.8,y:top,w:11.7,h:5.8-top});
      const selected=s.highlightIndex??s.values.indexOf(Math.max(...s.values));
      const fallback=[],orig=c.elements.length,row=(5.25-top)/s.values.length,max=Math.max(...s.values);
      s.labels.forEach((label,j)=>{
        const y=top+.3+j*row;
        text(label,1.1,y,3.45,.6,18,{role:'label',background:colors.surface});
        if(s.values[j]) c.rect(4.9,y+.05,5.6*s.values[j]/max,.25,j===selected?colors.accent:colors.foreground,'ResultsSlide','bar','data');
        text(String(s.values[j]),10.95,y,.95,.4,18,{role:'label',background:colors.surface});
      });
      text(s.unit,4.9,5.28,6.65,.35,18,{role:'label',background:colors.surface,color:theme.readableMuted});
      fallback.push(...c.elements.splice(orig));
      c.elements.push({kind:'chart',x:1,y:top+.15,w:11.25,h:5.6-top,labels:s.labels,values:s.values,unit:s.unit,
        colors:s.labels.map((_,j)=>j===selected?colors.accent:colors.foreground),color:colors.foreground,
        background:colors.surface,font:fonts.resolved.body,role:'chart',fallback,component:'ResultsSlide'});
      text(s.caption,.85,6.08,11.6,.7,20,{color:theme.readableMuted});
    } else if(layout==='equation') {
      PixelCard(c,{x:.8,y:top,w:11.7,h:1.35});
      text(s.equation,1.05,top+.35,11.2,.7,24,{color:colors.accent,background:colors.surface});
      bullets(s.bullets,{x:1,y:top+1.8,w:11.2,h:6.75-top-1.8},20);
    } else if(layout==='scatter') {
      PixelCard(c,{x:.8,y:top,w:8.4,h:6.25-top});
      const groups=[...new Set(s.points.map(p=>p.group))],palette=[colors.accent,colors.foreground,theme.readableMuted];
      const xs=s.points.map(p=>p.x),ys=s.points.map(p=>p.y),lx=Math.min(...xs),ly=Math.min(...ys),dx=Math.max(...xs)-lx||1,dy=Math.max(...ys)-ly||1;
      for(const p of s.points) c.rect(1.2+(p.x-lx)/dx*7.25,top+.3+(1-(p.y-ly)/dy)*(5.2-top),.1,.1,palette[groups.indexOf(p.group)%3],'PixelDiagram','point','data');
      groups.forEach((g,j)=>text(g,9.6,top+.25+j*.65,2.75,.55,18,{role:'label',color:palette[j%3]}));
      text(s.yLabel,9.6,5.4,2.75,.7,18,{role:'label',color:theme.readableMuted});
      text(s.xLabel,1.1,6.38,11.1,.36,18,{role:'label',color:theme.readableMuted});
      text(s.caption,1,6.82,11.3,.26,12,{role:'footer',color:theme.readableMuted});
    } else if(layout==='figure') {
      PixelCard(c,{x:.8,y:top,w:11.7,h:5.7-top});
      c.image(s.path,1.15,top+.2,11,5.3-top,s.alt,'PixelWindow');
      text(s.caption,.85,5.98,11.6,.72,20);
      text(s.attribution,.85,6.79,11.6,.24,12,{role:'footer',color:theme.readableMuted});
    } else if(layout==='references') {
      const row=(6.8-top)/s.ids.length;
      s.ids.forEach((id,j)=>{
        const r=spec.references.find(r=>r.id===id),y=top+j*row;
        const ref=text(`[${id}] ${r.text}`,1,y,11.1,row-.65,16,{role:'reference'});
        ref.h=Math.min(ref.h,ref.text.split('\n').length*16*1.23/72+.02);
        text(r.url,1,y+ref.h+.12,11.1,.45,14,{role:'reference',color:theme.readableMuted,url:r.url.startsWith('http')?r.url:undefined});
      });
    }
    scene.slides.push({background:colors.background,elements:c.elements,notes:s.notes||'',title:s.title});
  });
  return scene;
}
