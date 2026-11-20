import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
export function available() {
  try { require.resolve('pptxgenjs'); return true; } catch { return false; }
}
export async function writePptx(scene, target) {
  const PptxGenJS = require('pptxgenjs');
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.author = 'Slides Creator'; pptx.subject = 'Scientific and technical presentation';
  pptx.title = scene.title; pptx.lang = scene.language;
  pptx.theme = {headFontFace:'Liberation Sans',bodyFontFace:'Liberation Sans',lang:scene.language};
  for(const s of scene.slides) {
    const slide=pptx.addSlide(); slide.background={color:s.background};
    for(const e of s.elements) {
      const pos={x:e.x,y:e.y,w:e.w,h:e.h};
      if(e.kind==='text') slide.addText(e.text,{...pos,fontFace:e.font,fontSize:e.fontSize,color:e.color,bold:e.bold||false,
        margin:0,breakLine:false,valign:'top',fit:'none',lineSpacingMultiple:1.1,lang:scene.language,
        ...(e.url?{hyperlink:{url:e.url}}:{})});
      if(e.kind==='shape') slide.addShape(pptx.ShapeType[e.shape],{...pos,fill:{color:e.fill},line:{color:e.fill,transparency:100}});
      if(e.kind==='image') slide.addImage({path:e.path,...pos,sizing:{type:'contain',w:e.w,h:e.h},altText:e.alt});
      if(e.kind==='chart') slide.addChart(pptx.ChartType.bar,[{name:e.unit,labels:e.labels,values:e.values}],{
        ...pos,barDir:'bar',showLegend:false,showValue:true,showTitle:false,catAxisLabelFontSize:18,valAxisLabelFontSize:18,
        dataLabelFormatCode:'0.##',dataLabelPosition:'outEnd',dataLabelColor:e.color,dataLabelBkgrdColor:e.background,
        chartColors:e.colors,showBorder:false,showCatName:false,
        catAxisLabelColor:e.color,valAxisLabelColor:e.color,showSerName:false,
        chartArea:{fill:{color:e.background}},plotArea:{fill:{color:e.background}},
        valAxisTitle:e.unit,showValAxisTitle:true,valAxisTitleFontSize:18,valAxisTitleColor:e.color,
        dataLabelFontSize:18,catAxisLabelFontFace:e.font,valAxisLabelFontFace:e.font
      });
    }
    if(s.notes) slide.addNotes(s.notes);
  }
  await pptx.writeFile({fileName:target});
}
