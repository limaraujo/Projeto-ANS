#!/usr/bin/env python3
"""PDF converter for this skill's small OOXML subset, using installed Cairo/Pango.

Reads the PPTX package itself, not the input scene. Unsupported OOXML is rejected.
This is an explicit portability fallback, not a replacement for Office compatibility tests.
"""
import ctypes as C
import ctypes.util
from pathlib import Path
import posixpath
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from office import NS, EMU

Ptr, D, I = C.c_void_p, C.c_double, C.c_int


def library(name):
    found=C.util.find_library(name)
    if not found:
        raise RuntimeError('Biblioteca necessária ao conversor nativo: '+name)
    return C.CDLL(found)


def fn(lib,name,result,args):
    f=getattr(lib,name); f.restype=result; f.argtypes=args
    return f


class Rectangle(C.Structure):
    _fields_=[('x',D),('y',D),('width',D),('height',D)]


class Painter:
    def __init__(self,target,w,h):
        self.c=library('cairo'); self.p=library('pango-1.0'); self.pc=library('pangocairo-1.0'); self.g=library('gobject-2.0')
        self.surface=fn(self.c,'cairo_pdf_surface_create',Ptr,[C.c_char_p,D,D])(str(target).encode(),w,h)
        self.ctx=fn(self.c,'cairo_create',Ptr,[Ptr])(self.surface)
        signatures={
            'set_source_rgb':(None,[Ptr,D,D,D]),'paint':(None,[Ptr]),'rectangle':(None,[Ptr,D,D,D,D]),
            'fill':(None,[Ptr]),'new_path':(None,[Ptr]),'save':(None,[Ptr]),'restore':(None,[Ptr]),'translate':(None,[Ptr,D,D]),
            'scale':(None,[Ptr,D,D]),'arc':(None,[Ptr,D,D,D,D,D]),'move_to':(None,[Ptr,D,D]),
            'line_to':(None,[Ptr,D,D]),'close_path':(None,[Ptr]),'clip':(None,[Ptr]),'show_page':(None,[Ptr]),
            'status':(I,[Ptr]),'destroy':(None,[Ptr]),'surface_finish':(None,[Ptr]),
            'surface_status':(I,[Ptr]),'surface_destroy':(None,[Ptr]),
            'image_surface_create_from_png':(Ptr,[C.c_char_p]),'image_surface_get_width':(I,[Ptr]),
            'image_surface_get_height':(I,[Ptr]),'set_source_surface':(None,[Ptr,Ptr,D,D])}
        for name,(result,args) in signatures.items():
            setattr(self,name,fn(self.c,'cairo_'+name,result,args))
        self.new_layout=fn(self.pc,'pango_cairo_create_layout',Ptr,[Ptr])
        self.show_layout=fn(self.pc,'pango_cairo_show_layout',None,[Ptr,Ptr])
        self.layout_context=fn(self.p,'pango_layout_get_context',Ptr,[Ptr])
        self.resolution=fn(self.pc,'pango_cairo_context_set_resolution',None,[Ptr,D])
        self.font_parse=fn(self.p,'pango_font_description_from_string',Ptr,[C.c_char_p])
        self.font_free=fn(self.p,'pango_font_description_free',None,[Ptr])
        self.font_set=fn(self.p,'pango_layout_set_font_description',None,[Ptr,Ptr])
        self.text_set=fn(self.p,'pango_layout_set_text',None,[Ptr,C.c_char_p,I])
        self.unref=fn(self.g,'g_object_unref',None,[Ptr])

    def color(self,hex_value):
        rgb=[int(hex_value[i:i+2],16)/255 for i in (0,2,4)]
        self.set_source_rgb(self.ctx,*rgb)

    def text(self,value,x,y,font,size,bold,color):
        layout=self.new_layout(self.ctx)
        self.resolution(self.layout_context(layout),72)
        desc=self.font_parse(f'{font} {"Bold " if bold else ""}{size:g}'.encode())
        self.font_set(layout,desc); self.text_set(layout,value.encode(),-1)
        self.color(color); self.move_to(self.ctx,x,y); self.show_layout(self.ctx,layout)
        self.font_free(desc); self.unref(layout)

    def image(self,data,extension,x,y,w,h):
        self.save(self.ctx); self.translate(self.ctx,x,y)
        try:
            if extension=='.svg':
                rsvg=library('rsvg-2')
                handle=fn(rsvg,'rsvg_handle_new_from_data',Ptr,[C.c_char_p,C.c_size_t,Ptr])(data,len(data),None)
                if not handle:
                    raise RuntimeError('SVG inválido')
                viewport=Rectangle(0,0,w,h)
                ok=fn(rsvg,'rsvg_handle_render_document',I,[Ptr,Ptr,C.POINTER(Rectangle),Ptr])(handle,self.ctx,C.byref(viewport),None)
                self.unref(handle)
                if not ok:
                    raise RuntimeError('Falha na renderização SVG')
            else:
                with tempfile.TemporaryDirectory(prefix='slides-native-img-') as tmp:
                    file=Path(tmp)/'image.png'
                    if extension=='.png':
                        file.write_bytes(data)
                    else:
                        try:
                            from PIL import Image
                            import io
                            Image.open(io.BytesIO(data)).save(file)
                        except ImportError as e:
                            raise RuntimeError('JPEG no conversor nativo exige Pillow existente; use PNG/SVG ou LibreOffice') from e
                    surface=self.image_surface_create_from_png(str(file).encode())
                    if self.surface_status(surface):
                        raise RuntimeError('PNG inválido')
                    iw,ih=self.image_surface_get_width(surface),self.image_surface_get_height(surface)
                    self.scale(self.ctx,w/iw,h/ih); self.set_source_surface(self.ctx,surface,0,0);self.paint(self.ctx)
                    self.surface_destroy(surface)
        finally:
            self.restore(self.ctx)

    def finish(self):
        error=self.status(self.ctx)
        self.destroy(self.ctx);self.surface_finish(self.surface)
        error=error or self.surface_status(self.surface)
        self.surface_destroy(self.surface)
        if error:
            raise RuntimeError('Erro Cairo: '+str(error))


def convert(pptx,target):
    with zipfile.ZipFile(pptx) as z:
        presentation=ET.fromstring(z.read('ppt/presentation.xml'))
        size=presentation.find('p:sldSz',NS)
        width,height=int(size.get('cx'))/EMU*72,int(size.get('cy'))/EMU*72
        relations=ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
        targets={r.get('Id'):posixpath.normpath('ppt/'+r.get('Target')) for r in relations}
        pages=presentation.findall('p:sldIdLst/p:sldId',NS)
        painter=Painter(target,width,height)
        try:
            for page in pages:
                name=targets[page.get('{'+NS['r']+'}id')]
                root=ET.fromstring(z.read(name))
                background=root.find('.//p:bg//a:srgbClr',NS)
                painter.color(background.get('val') if background is not None else 'FFFFFF');painter.paint(painter.ctx)
                relname=posixpath.dirname(name)+'/_rels/'+posixpath.basename(name)+'.rels'
                slide_rels={r.get('Id'):posixpath.normpath(posixpath.join(posixpath.dirname(name),r.get('Target'))) for r in ET.fromstring(z.read(relname)) if r.get('TargetMode')!='External'}
                for element in root.find('p:cSld/p:spTree',NS):
                    tag=element.tag.split('}')[-1]
                    if tag in ('nvGrpSpPr','grpSpPr'):
                        continue
                    if tag not in ('sp','pic'):
                        raise RuntimeError(f'Conversor nativo não suporta {tag}; use LibreOffice')
                    props=element.find('p:spPr',NS)
                    transform=props.find('a:xfrm',NS) if props is not None else None
                    if transform is None or transform.get('rot'):
                        raise RuntimeError('Transformação OOXML não suportada; use LibreOffice')
                    off,extent=transform.find('a:off',NS),transform.find('a:ext',NS)
                    x,y,w,h=[int(v)/EMU*72 for v in (off.get('x'),off.get('y'),extent.get('cx'),extent.get('cy'))]
                    if tag=='pic':
                        blip=element.find('p:blipFill/a:blip',NS)
                        media=slide_rels[blip.get('{'+NS['r']+'}embed')]
                        painter.image(z.read(media),Path(media).suffix.lower(),x,y,w,h)
                        continue
                    geom=props.find('a:prstGeom',NS)
                    shape=geom.get('prst') if geom is not None else None
                    fill=props.find('a:solidFill/a:srgbClr',NS)
                    if shape not in ('rect','ellipse','chevron'):
                        raise RuntimeError('Forma OOXML não suportada: '+str(shape))
                    if fill is not None:
                        painter.new_path(painter.ctx)
                        painter.color(fill.get('val'))
                        if shape=='rect':
                            painter.rectangle(painter.ctx,x,y,w,h)
                        elif shape=='ellipse':
                            painter.save(painter.ctx);painter.translate(painter.ctx,x+w/2,y+h/2);painter.scale(painter.ctx,w/2,h/2)
                            painter.arc(painter.ctx,0,0,1,0,6.283185307179586);painter.restore(painter.ctx)
                        else:
                            points=[(x,y),(x+w*.6,y),(x+w,y+h/2),(x+w*.6,y+h),(x,y+h),(x+w*.4,y+h/2)]
                            painter.move_to(painter.ctx,*points[0])
                            for pt in points[1:]: painter.line_to(painter.ctx,*pt)
                            painter.close_path(painter.ctx)
                        painter.fill(painter.ctx)
                    body=element.find('p:txBody',NS)
                    if body is None:
                        continue
                    painter.save(painter.ctx);painter.rectangle(painter.ctx,x,y,w,h);painter.clip(painter.ctx)
                    yy=y
                    for paragraph in body.findall('a:p',NS):
                        runs=paragraph.findall('a:r',NS)
                        if len(runs)!=1:
                            raise RuntimeError('Conversor nativo exige um run por parágrafo; use LibreOffice')
                        run=runs[0];options=run.find('a:rPr',NS);latin=options.find('a:latin',NS);color=options.find('a:solidFill/a:srgbClr',NS)
                        font_size=int(options.get('sz'))/100
                        painter.text(run.findtext('a:t','',NS),x,yy,latin.get('typeface'),font_size,options.get('b')=='1',color.get('val'))
                        spacing=paragraph.find('a:pPr/a:lnSpc/a:spcPct',NS)
                        yy+=font_size*(int(spacing.get('val'))/100000 if spacing is not None else 1.1)
                    painter.restore(painter.ctx)
                painter.show_page(painter.ctx)
        finally:
            painter.finish()
    return {'pdf':str(target),'engine':'native-subset','pages':len(pages),
            'limitation':'Cairo/Pango conversion of supported editable OOXML only; LibreOffice/PowerPoint compatibility is not established by this export.'}
