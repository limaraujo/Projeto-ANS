import {spawnSync} from 'node:child_process';

// fc-match can return a substitute. Verify the actual family, not just its exit code.
export function installedFamily(family) {
  const result=spawnSync('fc-match',['-f','%{family}',family],{encoding:'utf8',timeout:5000});
  if(result.status!==0 || !result.stdout) return false;
  return result.stdout.split(',').some(name=>name.trim().toLowerCase()===family.toLowerCase());
}
export function resolveFonts(profile, probe=installedFamily) {
  const requested=profile.typography, resolved={}, warnings=[];
  for(const [role,family] of Object.entries(requested)) {
    if(probe(family)) resolved[role]=family;
    else {
      const fallback=profile.fallbacks[role];
      if(!probe(fallback)) throw new Error(`Fonte ${family} ausente; fallback ${fallback} também indisponível. Instale uma das fontes ou configure Fontconfig.`);
      resolved[role]=fallback; warnings.push(`${role}: ${family} ausente; usando ${fallback}.`);
    }
  }
  return {requested,resolved,warnings,embedded:false};
}
