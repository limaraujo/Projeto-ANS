#!/usr/bin/env python3
"""Convert through LibreOfficeKit's stable C API, without a desktop IPC listener.

ABI prefix documented in LibreOffice's include/LibreOfficeKit/LibreOfficeKit.h.
This uses the installed engine; it does not emulate export or intercept system calls.
"""
import argparse
import ctypes as C
import json
from pathlib import Path

Ptr = C.c_void_p
Destroy = C.CFUNCTYPE(None, Ptr)
Load = C.CFUNCTYPE(Ptr, Ptr, C.c_char_p)
Error = C.CFUNCTYPE(Ptr, Ptr)
LoadOptions = C.CFUNCTYPE(Ptr, Ptr, C.c_char_p, C.c_char_p)
Free = C.CFUNCTYPE(None, Ptr)
Save = C.CFUNCTYPE(C.c_int, Ptr, C.c_char_p, C.c_char_p, C.c_char_p)


class Instance(C.Structure):
    _fields_ = [('pClass', Ptr)]


class OfficeClass(C.Structure):
    _fields_ = [('nSize', C.c_size_t), ('destroy', Destroy), ('documentLoad', Load),
                ('getError', Error), ('documentLoadWithOptions', LoadOptions), ('freeError', Free)]


class DocumentClass(C.Structure):
    _fields_ = [('nSize', C.c_size_t), ('destroy', Destroy), ('saveAs', Save)]


def api(instance, klass):
    pointer = C.cast(instance, C.POINTER(Instance)).contents.pClass
    result = C.cast(pointer, C.POINTER(klass)).contents
    if result.nSize < C.sizeof(klass):
        raise RuntimeError('ABI LibreOfficeKit antiga/incompatível')
    return result


def convert(program, profile, pptx, target):
    library = next((Path(program)/name for name in ('libsofficeapp.so','libmergedlo.so')
                    if (Path(program)/name).is_file() and (Path(program)/name).stat().st_size>1000), None)
    if not library:
        raise RuntimeError('Biblioteca LibreOfficeKit indisponível')
    lib = C.CDLL(str(library), mode=C.RTLD_GLOBAL)
    init = lib.libreofficekit_hook_2
    init.argtypes, init.restype = [C.c_char_p, C.c_char_p], Ptr
    kit = init(str(program).encode(), profile.encode())
    if not kit:
        raise RuntimeError('LibreOfficeKit não inicializou')
    office = api(kit, OfficeClass)
    document = None
    try:
        document = office.documentLoad(kit, Path(pptx).resolve().as_uri().encode())
        if not document:
            error = office.getError(kit)
            message = C.string_at(error).decode(errors='replace') if error else 'erro desconhecido'
            if error:
                office.freeError(error)
            raise RuntimeError('LibreOfficeKit não abriu PPTX: '+message)
        doc = api(document, DocumentClass)
        if not doc.saveAs(document, Path(target).resolve().as_uri().encode(), b'pdf', b''):
            raise RuntimeError('LibreOfficeKit falhou ao exportar PDF')
    finally:
        if document:
            api(document, DocumentClass).destroy(document)
        office.destroy(kit)
    if not Path(target).is_file() or Path(target).stat().st_size<100:
        raise RuntimeError('LibreOfficeKit não produziu PDF válido')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ('program','profile','pptx','out'):
        parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    convert(args.program,args.profile,args.pptx,args.out)
    print(json.dumps({'pdf':args.out,'method':'LibreOfficeKit stable C API'}))
