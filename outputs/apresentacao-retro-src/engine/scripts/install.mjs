#!/usr/bin/env node
// Run from an environment that permits writing the requested destination.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { ROOT } from './model.mjs';
const args=process.argv.slice(2);
if(args.length && (args.length!==2 || args[0]!=='--dest')) throw new Error('Uso: node scripts/install.mjs [--dest /projeto/.agents/skills/slides-creator]');
const dest=path.resolve(args[1]||path.join(os.homedir(),'.agents/skills/slides-creator'));
if(path.basename(dest)!=='slides-creator') throw new Error('Destino deve terminar em slides-creator');
if(dest===ROOT || dest.startsWith(ROOT+path.sep)) throw new Error('Escolha um destino fora da pasta de origem da skill');
if(fs.existsSync(dest)) throw new Error('Destino já existe; não será sobrescrito');
fs.mkdirSync(path.dirname(dest),{recursive:true});
const staging=fs.mkdtempSync(path.join(path.dirname(dest),'.slides-creator-install-'));
try {
  fs.cpSync(ROOT,staging,{recursive:true,filter:src=>!['node_modules','outputs','__pycache__','.git'].includes(path.basename(src))});
  fs.renameSync(staging,dest);
} catch(e) { fs.rmSync(staging,{recursive:true,force:true}); throw e; }
console.log(`Skill instalada em ${dest}\nFunciona offline com OOXML. Para PptxGenJS: npm --prefix "${dest}" install --no-audit --no-fund`);
