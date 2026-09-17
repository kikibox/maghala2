#!/usr/bin/env python3
from pathlib import Path

path=Path(__file__).with_name('build_patch.py')
lines=[]
for line in path.read_text(encoding='utf-8').splitlines():
    stripped=line.lstrip()
    indent=line[:len(line)-len(stripped)]
    if stripped.startswith("new=f'"):
        line=indent+"new='https://'+'navar-abyari.ir/'+PREFIX[lang]+'/'+target+'/'"
    if "values=[post_id,1," in line:
        bad="f'{{https://navar-abyari.ir/?p={post_id}}}'"
        line=line.replace(bad,"'https://'+'navar-abyari.ir/?p='+str(post_id)")
    lines.append(line)
source='\n'.join(lines)+'\n'
compile(source,str(path),'exec')
namespace={'__name__':'__main__','__file__':str(path)}
exec(compile(source,str(path),'exec'),namespace)
