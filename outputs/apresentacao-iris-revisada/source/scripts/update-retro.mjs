#!/usr/bin/env node
// Incremental update of an existing installation. Run where the target is writable.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {ROOT} from './model.mjs';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
export function updateRetro(dest=path.join(os.homedir(),'.agents/skills/slides-creator'),dryRun=false) {
  dest=path.resolve(dest);
  if(dest===ROOT||dest.startsWith(ROOT+path.sep)) throw new Error('Use uma instalação existente fora da pasta de origem.');
  if(!fs.existsSync(path.join(dest,'SKILL.md'))) throw new Error('Skill existente não encontrada no destino; este comando não reinstala a skill.');
  const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'scripts/update-retro.json'),'utf8'));
  const pending=[];
  // Preflight every change before touching the installation.
  for(const [file,baseline] of Object.entries(manifest.files)) {
    const source=fs.readFileSync(path.join(ROOT,file)),target=path.join(dest,file);
    const current=fs.existsSync(target)?fs.readFileSync(target):null;
    if(current&&hash(current)===hash(source)) continue;
    if(current ? baseline===null||hash(current)!==baseline : baseline!==null) throw new Error(`Alterações locais ou versão incompatível em ${file}; mescle esse arquivo antes de atualizar. Nenhum arquivo foi alterado.`);
    pending.push({file,bytes:source,current});
  }
  const profileFile='assets/templates/profiles.json';
  const oldBytes=fs.readFileSync(path.join(dest,profileFile)),original=JSON.parse(oldBytes),sourceProfiles=JSON.parse(fs.readFileSync(path.join(ROOT,profileFile)));
  if(original['retroui-pixel']&&JSON.stringify(original['retroui-pixel'])!==JSON.stringify(sourceProfiles['retroui-pixel'])) throw new Error('O tema retroui-pixel instalado contém alterações locais; atualização interrompida.');
  if(!original['retroui-pixel']) {
    original['retroui-pixel']=sourceProfiles['retroui-pixel'];
    pending.push({file:profileFile,bytes:Buffer.from(JSON.stringify(original,null,2)+'\n'),current:oldBytes});
  }
  if(!dryRun) for(const {file,bytes,current} of pending) {
    const target=path.join(dest,file),backup=path.join(dest,'.retroui-pixel-backup',file);
    if(current&&!fs.existsSync(backup)) {fs.mkdirSync(path.dirname(backup),{recursive:true});fs.writeFileSync(backup,current,{flag:'wx'});}
    fs.mkdirSync(path.dirname(target),{recursive:true});
    const temp=target+`.retro-${process.pid}.tmp`;
    try {fs.writeFileSync(temp,bytes,{flag:'wx'});fs.renameSync(temp,target);}
    finally {fs.rmSync(temp,{force:true});}
  }
  return {dest,dryRun,files:pending.map(p=>p.file),message:pending.length?(dryRun?'Atualização preparada; nenhum arquivo alterado.':'Tema integrado; arquivos anteriores guardados em .retroui-pixel-backup.'):'Instalação já atualizada.'};
}
if(process.argv[1]&&fs.existsSync(process.argv[1])&&import.meta.url===pathToFileURL(fs.realpathSync(process.argv[1])).href) {
  try {
    const args=process.argv.slice(2);let dest,dry=false;
    for(let i=0;i<args.length;i++) {
      if(args[i]==='--dry-run') dry=true;
      else if(args[i]==='--dest'&&args[i+1]) dest=args[++i];
      else throw new Error('Uso: node scripts/update-retro.mjs [--dest /skill/existente] [--dry-run]');
    }
    console.log(JSON.stringify(updateRetro(dest,dry),null,2));
  } catch(error) {console.error(error.message);process.exitCode=1;}
}
