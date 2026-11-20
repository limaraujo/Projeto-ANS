#!/usr/bin/env python3
"""Offline OOXML writer and real LibreOffice/Poppler verification. Python stdlib only."""
import argparse
import collections
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import struct
import subprocess
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, quoteattr
import zipfile
import ctypes.util

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'a': A, 'p': P, 'r': R}
EMU = 914400
DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'


def run(args, env=None, timeout=120):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True,
                            timeout=timeout, env=env)
    if result.returncode:
        raise RuntimeError(f'{args[0]} (exit {result.returncode}): {(result.stderr or result.stdout).strip()[:1500]}')
    return result.stdout


def office():
    """Prefer an explicit executable, then normal installs; use existing Snap libraries if needed."""
    explicit = os.environ.get('SOFFICE')
    candidates = [(explicit, {})] if explicit else []
    if not explicit:
        candidates += [(shutil.which(x), {}) for x in ('libreoffice', 'soffice')]
        snap = Path('/snap/libreoffice/current')
        executable = snap / 'lib/libreoffice/program/soffice'
        if executable.exists():
            libs = [snap / 'usr/lib/x86_64-linux-gnu',
                    Path('/snap/mesa-2404/current/usr/lib/x86_64-linux-gnu')]
            ld = ':'.join(str(x) for x in libs if x.is_dir())
            if os.environ.get('LD_LIBRARY_PATH'):
                ld += ':' + os.environ['LD_LIBRARY_PATH']
            candidates.append((str(executable), {'LD_LIBRARY_PATH': ld}))
    failures = []
    for executable, extra in candidates:
        if not executable:
            continue
        env = dict(os.environ, SAL_USE_VCLPLUGIN='svp', **extra)
        try:
            version = run([executable, '--headless', '--version'], env, 15).strip()
            return executable, env, version
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as e:
            failures.append(str(e))
    raise RuntimeError('LibreOffice indisponível. Defina SOFFICE ou instale LibreOffice Impress. ' + ' | '.join(failures))


def doctor():
    result = {'python': os.sys.version.split()[0], 'tools': {}}
    for name in ('pdftoppm', 'pdftotext', 'pdfinfo'):
        result['tools'][name] = shutil.which(name)
    try:
        exe, _, version = office()
        result['libreoffice'] = {'path': exe, 'version': version}
    except RuntimeError as e:
        result['libreoffice'] = {'error': str(e)}
    result['nativePdf'] = all(ctypes.util.find_library(x) for x in ('cairo','pango-1.0','pangocairo-1.0','rsvg-2','gobject-2.0'))
    result['ready'] = all(result['tools'].values()) and ('error' not in result['libreoffice'] or result['nativePdf'])
    result['note'] = 'Version detection does not establish successful document conversion. Run integration tests.'
    return result


def rels(items):
    return DECL + f'<Relationships xmlns="{REL}">' + ''.join(
        f'<Relationship Id="{rid}" Type="{R}/{kind}" Target={quoteattr(target)}'
        + (' TargetMode="External"' if external else '') + '/>'
        for rid, kind, target, external in items) + '</Relationships>'


def group():
    return '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'


def xfrm(e):
    return f'<a:xfrm><a:off x="{round(e["x"]*EMU)}" y="{round(e["y"]*EMU)}"/><a:ext cx="{round(e["w"]*EMU)}" cy="{round(e["h"]*EMU)}"/></a:xfrm>'


def shape(e, idx, link_id=None):
    is_text = e['kind'] == 'text'
    geom = 'rect' if is_text else e.get('shape', 'rect')
    props = xfrm(e) + f'<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>'
    props += (f'<a:solidFill><a:srgbClr val="{e["fill"]}"/></a:solidFill>' if e.get('fill') else '<a:noFill/>')
    props += '<a:ln><a:noFill/></a:ln>'
    body = ''
    if is_text:
        size = round(e['fontSize'] * 100)
        attrs = f'lang="{escape(e.get("language", "pt-BR"))}" sz="{size}" b="{int(e.get("bold", False))}"'
        hlink = f'<a:hlinkClick r:id="{link_id}"/>' if link_id else ''
        paragraphs = []
        for line in e['text'].split('\n'):
            paragraphs.append('<a:p><a:pPr><a:lnSpc><a:spcPct val="110000"/></a:lnSpc></a:pPr>'
                              f'<a:r><a:rPr {attrs}><a:solidFill><a:srgbClr val="{e["color"]}"/></a:solidFill>'
                              f'<a:latin typeface={quoteattr(e["font"])}/><a:ea typeface={quoteattr(e["font"])}/>'
                              f'<a:cs typeface={quoteattr(e["font"])}/>{hlink}</a:rPr>'
                              f'<a:t xml:space="preserve">{escape(line)}</a:t></a:r>'
                              f'<a:endParaRPr {attrs}/></a:p>')
        body = '<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/>' + ''.join(paragraphs) + '</p:txBody>'
    return f'<p:sp><p:nvSpPr><p:cNvPr id="{idx}" name="Element {idx}"/><p:cNvSpPr txBox="{int(is_text)}"/><p:nvPr/></p:nvSpPr><p:spPr>{props}</p:spPr>{body}</p:sp>'


def image_size(file):
    data = Path(file).read_bytes()
    if data.startswith(b'\x89PNG'):
        return struct.unpack('>II', data[16:24])
    if Path(file).suffix.lower() == '.svg':
        root = ET.fromstring(data)
        view = root.get('viewBox', '').split()
        if len(view) == 4:
            return float(view[2]), float(view[3])
        return float(re.sub(r'[^0-9.]', '', root.get('width', '1'))), float(re.sub(r'[^0-9.]', '', root.get('height', '1')))
    if data.startswith(b'\xff\xd8'):
        pos = 2
        while pos < len(data)-10:
            if data[pos] != 255:
                pos += 1
                continue
            marker = data[pos+1]
            length = int.from_bytes(data[pos+2:pos+4], 'big')
            if marker in (0xc0, 0xc1, 0xc2):
                return int.from_bytes(data[pos+7:pos+9], 'big'), int.from_bytes(data[pos+5:pos+7], 'big')
            pos += length+2
    raise ValueError(f'Dimensões da imagem não reconhecidas: {file}')


def picture(e, idx, rid):
    iw, ih = image_size(e['path'])
    scale = min(e['w']/iw, e['h']/ih)
    fitted = dict(e, x=e['x']+(e['w']-iw*scale)/2, y=e['y']+(e['h']-ih*scale)/2,
                  w=iw*scale, h=ih*scale)
    return (f'<p:pic><p:nvPicPr><p:cNvPr id="{idx}" name="Image {idx}" descr={quoteattr(e["alt"])}/>'
            '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            f'<p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            f'<p:spPr>{xfrm(fitted)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')


def write_pptx(scene, target):
    """Create an OPC package with master, layout, theme, editable shapes and speaker notes."""
    parts = {}
    overrides = {}
    def put(name, value, content_type=None):
        parts[name] = value
        if content_type:
            overrides['/'+name] = content_type
    mime = 'application/vnd.openxmlformats-officedocument.presentationml.'
    root_attrs = f'xmlns:a="{A}" xmlns:r="{R}" xmlns:p="{P}"'
    put('_rels/.rels', rels([('rId1','officeDocument','ppt/presentation.xml',False)]))
    sids = ''.join(f'<p:sldId id="{256+i}" r:id="rId{i+2}"/>' for i in range(len(scene['slides'])))
    put('ppt/presentation.xml', DECL + f'<p:presentation {root_attrs}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        f'<p:sldIdLst>{sids}</p:sldIdLst><p:sldSz cx="{round(scene["w"]*EMU)}" cy="{round(scene["h"]*EMU)}" type="screen16x9"/>'
        '<p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>', mime+'presentation.main+xml')
    put('ppt/_rels/presentation.xml.rels', rels([('rId1','slideMaster','slideMasters/slideMaster1.xml',False)] +
        [(f'rId{i+2}','slide',f'slides/slide{i+1}.xml',False) for i in range(len(scene['slides']))] +
        [('rIdNotes','notesMaster','notesMasters/notesMaster1.xml',False)]))
    # The notes master is declared explicitly so viewers can find editable speaker notes.
    parts['ppt/presentation.xml'] = parts['ppt/presentation.xml'].replace('<p:sldIdLst>', '<p:notesMasterIdLst><p:notesMasterId r:id="rIdNotes"/></p:notesMasterIdLst><p:sldIdLst>')
    cmap = '<p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/>'
    put('ppt/slideMasters/slideMaster1.xml', DECL + f'<p:sldMaster {root_attrs}><p:cSld><p:spTree>{group()}</p:spTree></p:cSld>{cmap}'
        '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>', mime+'slideMaster+xml')
    put('ppt/slideMasters/_rels/slideMaster1.xml.rels', rels([('rId1','slideLayout','../slideLayouts/slideLayout1.xml',False),('rId2','theme','../theme/theme1.xml',False)]))
    put('ppt/slideLayouts/slideLayout1.xml', DECL + f'<p:sldLayout {root_attrs} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{group()}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>', mime+'slideLayout+xml')
    put('ppt/slideLayouts/_rels/slideLayout1.xml.rels', rels([('rId1','slideMaster','../slideMasters/slideMaster1.xml',False)]))
    colors = ['172B40','FFFFFF','4B5B6B','F0F4F7','135E83','7A3E65','006B63','7B4C00','425D5A','67E8F9','135E83','7A3E65']
    names = ['dk1','lt1','dk2','lt2','accent1','accent2','accent3','accent4','accent5','accent6','hlink','folHlink']
    palette = ''.join(f'<a:{n}><a:srgbClr val="{c}"/></a:{n}>' for n,c in zip(names,colors))
    fill = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    put('ppt/theme/theme1.xml', DECL+f'<a:theme xmlns:a="{A}" name="Slides Creator"><a:themeElements><a:clrScheme name="Scientific">{palette}</a:clrScheme>'
        '<a:fontScheme name="Liberation"><a:majorFont><a:latin typeface="Liberation Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Liberation Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>'
        f'<a:fmtScheme name="Minimal"><a:fillStyleLst>{fill*3}</a:fillStyleLst><a:lnStyleLst>'
        + ''.join(f'<a:ln w="{v}">{fill}<a:prstDash val="solid"/></a:ln>' for v in (6350,12700,19050))
        + f'</a:lnStyleLst><a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>"*3}</a:effectStyleLst><a:bgFillStyleLst>{fill*3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>', 'application/vnd.openxmlformats-officedocument.theme+xml')
    put('ppt/notesMasters/notesMaster1.xml', DECL+f'<p:notesMaster {root_attrs}><p:cSld><p:spTree>{group()}</p:spTree></p:cSld>{cmap}<p:notesStyle/></p:notesMaster>', mime+'notesMaster+xml')
    put('ppt/notesMasters/_rels/notesMaster1.xml.rels', rels([('rId1','theme','../theme/theme1.xml',False)]))
    for i, slide in enumerate(scene['slides'], 1):
        relationships = [('rId1','slideLayout','../slideLayouts/slideLayout1.xml',False),('rId2','notesSlide',f'../notesSlides/notesSlide{i}.xml',False)]
        elements = []
        for e in slide['elements']:
            elements.extend(e['fallback'] if e['kind']=='chart' else [e])
        xml = []
        for idx,e in enumerate(elements,2):
            rid = f'rId{idx+10}'
            if e['kind']=='image':
                filename = f'image{i}-{idx}{Path(e["path"]).suffix.lower()}'
                put('ppt/media/'+filename, Path(e['path']).read_bytes())
                relationships.append((rid,'image','../media/'+filename,False))
                xml.append(picture(e,idx,rid))
            else:
                if e.get('url'):
                    relationships.append((rid,'hyperlink',e['url'],True))
                xml.append(shape(dict(e,language=scene['language']),idx,rid if e.get('url') else None))
        put(f'ppt/slides/slide{i}.xml', DECL+f'<p:sld {root_attrs}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="{slide["background"]}"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
            f'<p:spTree>{group()}{"".join(xml)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>', mime+'slide+xml')
        put(f'ppt/slides/_rels/slide{i}.xml.rels', rels(relationships))
        note = escape(slide.get('notes',''))
        put(f'ppt/notesSlides/notesSlide{i}.xml', DECL+f'<p:notes {root_attrs}><p:cSld><p:spTree>{group()}'
            '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/><p:cNvSpPr/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:t xml:space="preserve">{note}</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>', mime+'notesSlide+xml')
        put(f'ppt/notesSlides/_rels/notesSlide{i}.xml.rels', rels([('rId1','notesMaster','../notesMasters/notesMaster1.xml',False),('rId2','slide',f'../slides/slide{i}.xml',False)]))
    defaults = {'rels':'application/vnd.openxmlformats-package.relationships+xml','xml':'application/xml','png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','svg':'image/svg+xml'}
    put('[Content_Types].xml', DECL+'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        + ''.join(f'<Default Extension="{ext}" ContentType="{ct}"/>' for ext,ct in defaults.items())
        + ''.join(f'<Override PartName="{name}" ContentType="{ct}"/>' for name,ct in overrides.items())+'</Types>')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,value in parts.items():
            z.writestr(name,value)


def convert(pptx, out, engine='auto'):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    expected = out/(Path(pptx).stem+'.pdf')
    expected.unlink(missing_ok=True)  # A stale PDF must never pass a failed conversion.
    if engine not in ('auto','libreoffice','libreofficekit','native'):
        raise ValueError('pdf-engine: auto, libreoffice, libreofficekit ou native')
    failure = None
    if engine in ('auto','libreoffice','libreofficekit'):
        try:
            exe, env, version = office()
            with tempfile.TemporaryDirectory(prefix='slides-creator-lo-') as profile:
                env = dict(env, XDG_CACHE_HOME=profile)
                if engine=='libreofficekit':
                    program=Path(exe).resolve().parent
                    log=run([os.sys.executable,Path(__file__).with_name('lok.py'),'--program',program,
                             '--profile',Path(profile).as_uri(),'--pptx',Path(pptx).resolve(),'--out',expected],env)
                else:
                    log = run([exe, '-env:UserInstallation='+Path(profile).as_uri(), '--headless', '--nologo',
                               '--nodefault', '--nofirststartwizard', '--convert-to','pdf:impress_pdf_Export',
                               '--outdir',out,Path(pptx).resolve()],env)
            if not expected.is_file() or expected.stat().st_size < 100:
                raise RuntimeError('LibreOffice não produziu PDF: '+log)
            return {'pdf':str(expected),'libreoffice':version,'engine':engine if engine!='auto' else 'libreoffice','log':log.strip()}
        except (OSError,RuntimeError,subprocess.TimeoutExpired) as error:
            if engine!='auto':
                raise
            failure=str(error)
    from native_pdf import convert as native_convert
    result=native_convert(pptx,expected)
    if failure:
        result['fallbackReason']=failure
    if not expected.is_file() or expected.stat().st_size < 100:
        raise RuntimeError('Conversor não produziu PDF')
    return result


def render(pdf, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob('slide-*.png'):
        old.unlink()
    run(['pdftoppm','-png','-r','100',pdf,out/'slide'],timeout=180)
    images = sorted(out.glob('slide-*.png'),key=lambda p:int(p.stem.split('-')[-1]))
    if not images:
        raise RuntimeError('Poppler não produziu prévias')
    return [str(p) for p in images]


def integrity(pptx, scene):
    issues = []
    with zipfile.ZipFile(pptx) as z:
        if sum(i.file_size for i in z.infolist()) > 150_000_000 or len(z.infolist()) > 20000:
            raise ValueError('Arquivo excede limites do validador')
        bad = z.testzip()
        if bad:
            issues.append({'code':'zip-crc','message':bad})
        names = set(z.namelist())
        for required in ('[Content_Types].xml','_rels/.rels','ppt/presentation.xml'):
            if required not in names:
                raise ValueError('Parte obrigatória ausente: '+required)
        for name in names:
            if not (name.endswith('.xml') or name.endswith('.rels')):
                continue
            root = ET.fromstring(z.read(name))
            if name.endswith('.rels'):
                base = '' if name=='_rels/.rels' else posixpath.dirname(posixpath.dirname(name))
                for r in root:
                    if r.get('TargetMode')=='External':
                        continue
                    target = r.get('Target','')
                    resolved = posixpath.normpath(posixpath.join(base,target)) if not target.startswith('/') else target[1:]
                    if resolved not in names:
                        issues.append({'code':'broken-relationship','message':name+' -> '+target})
        slides = sorted(n for n in names if re.fullmatch(r'ppt/slides/slide\d+.xml',n))
        presentation=ET.fromstring(z.read('ppt/presentation.xml'))
        children=[e.tag.split('}')[-1] for e in presentation]
        order=['sldMasterIdLst','notesMasterIdLst','handoutMasterIdLst','sldIdLst','sldSz','notesSz','smartTags','embeddedFontLst','custShowLst','photoAlbum','custDataLst','kinsoku','defaultTextStyle','modifyVerifier','extLst']
        ranks=[order.index(name) for name in children if name in order]
        if ranks!=sorted(ranks):
            issues.append({'code':'presentation-order','message':'Ordem dos elementos de apresentação incompatível com OOXML'})
        count = len(presentation.findall('p:sldIdLst/p:sldId',NS))
        if count != len(scene['slides']) or len(slides) != count:
            issues.append({'code':'slide-count','message':f'Esperado {len(scene["slides"])}, encontrado {count} / {len(slides)}'})
        for name in slides:
            tree = ET.fromstring(z.read(name))
            if not tree.findall('.//a:t',NS):
                issues.append({'code':'no-editable-text','message':name})
            for x in tree.findall('.//a:xfrm',NS):
                off, ext = x.find('a:off',NS), x.find('a:ext',NS)
                if off is None or ext is None:
                    continue
                a,b,c,d = (int(off.get('x')),int(off.get('y')),int(ext.get('cx')),int(ext.get('cy')))
                if min(a,b,c,d)<0 or a+c>scene['w']*EMU+100 or b+d>scene['h']*EMU+100:
                    issues.append({'code':'ooxml-bounds','message':name})
    return issues


def normalized(s):
    return re.sub(r'\s+',' ',unicodedata.normalize('NFKC',s)).strip()


def validate(pptx, scene, pdf, previews):
    issues = integrity(pptx,scene)
    info = run(['pdfinfo',pdf])
    match = re.search(r'^Pages:\s+(\d+)',info,re.M)
    count = int(match.group(1)) if match else 0
    if count != len(scene['slides']):
        issues.append({'code':'pdf-page-count','message':f'PDF: {count} páginas'})
    pages = run(['pdftotext','-layout','-enc','UTF-8',pdf,'-']).split('\f')
    for i,s in enumerate(scene['slides']):
        actual = normalized(pages[i] if i<len(pages) else '')
        for e in s['elements']:
            if e['kind']=='text':
                # PDF reading order can interleave parallel columns; check composed lines separately.
                missing=[line for line in e['text'].split('\n') if normalized(line) and normalized(line) not in actual]
                if missing:
                    issues.append({'code':'rendered-text-missing','slide':i+1,'message':' | '.join(missing)[:180]})
    bbox = ET.fromstring(run(['pdftotext','-bbox',pdf,'-']))
    for page in bbox.iter():
        if page.tag.split('}')[-1] != 'page':
            continue
        w,h = float(page.get('width')),float(page.get('height'))
        for word in page.iter():
            if word.tag.split('}')[-1]=='word' and (float(word.get('xMin'))<-.1 or float(word.get('yMin'))<-.1 or float(word.get('xMax'))>w+.1 or float(word.get('yMax'))>h+.1):
                issues.append({'code':'pdf-word-bounds','message':word.text})
    images = list(Path(previews).glob('slide-*.png'))
    if len(images)!=len(scene['slides']):
        issues.append({'code':'preview-count','message':str(len(images))})
    for image in images:
        if not image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n') or image.stat().st_size<1000:
            issues.append({'code':'invalid-preview','message':str(image)})
    return {'issues':issues,'slideCount':len(scene['slides']),'pdfPages':count,'previewCount':len(images),
            'checks':['ZIP CRC','XML parse','OPC relationships','slide count','editable text','OOXML bounds',
                      'PDF page count','rendered text coverage','PDF word bounds','PNG count/signature']}


def extract(file, out):
    file, out = Path(file).resolve(), Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if file.suffix.lower()=='.pdf':
        text = run(['pdftotext','-layout','-enc','UTF-8',file,'-'])
        pages = text.split('\f')
        if not pages[-1].strip():
            pages.pop()
        text = '\n\n'.join(f'--- Página {i+1} ---\n{s}' for i,s in enumerate(pages))
        if sum(len(re.findall(r'\w',p)) for p in pages)<30:
            raise ValueError('PDF sem texto suficiente: OCR necessário; extração interrompida')
    elif file.suffix.lower() in ('.md','.markdown','.txt'):
        text = file.read_text(encoding='utf-8')
    else:
        raise ValueError('Entrada deve ser PDF, Markdown ou TXT')
    target = out/(file.stem+'.txt')
    if target.exists():
        raise ValueError('Extração não sobrescreve arquivo existente: '+str(target))
    target.write_text(text,encoding='utf-8')
    return {'source':str(file),'text':str(target),'characters':len(text)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['doctor','write','convert','render','validate','extract','integrity'])
    for key in ('scene','pptx','pdf','out','previews','input','engine'):
        parser.add_argument('--'+key)
    args=parser.parse_args()
    scene=json.loads(Path(args.scene).read_text()) if args.scene else None
    if args.command=='doctor':
        result=doctor()
    elif args.command=='write':
        write_pptx(scene,args.out); result={'pptx':args.out}
    elif args.command=='convert':
        result=convert(args.pptx,args.out,args.engine or 'auto')
    elif args.command=='render':
        result={'images':render(args.pdf,args.out)}
    elif args.command=='validate':
        result=validate(args.pptx,scene,args.pdf,args.previews)
    elif args.command=='integrity':
        result={'issues':integrity(args.pptx,scene)}
    else:
        result=extract(args.input,args.out)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'error':str(error)},ensure_ascii=False),file=os.sys.stderr)
        os.sys.exit(1)
