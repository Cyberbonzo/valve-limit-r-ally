from pathlib import Path
import os,json,subprocess,hashlib,re
from progress import prepare,backup
r=Path(__file__).resolve().parents[1]
if hashlib.sha256((r/'game/launcher.exe').read_bytes()).hexdigest()!='f3cfe44a82b16d935d8e6dc46c83cb9893483c2b6018d65e4ed911063061d70e':raise SystemExit('Unsupported launcher.exe revision')
manifest=json.loads((r/'docs/hd-build.json').read_text())
if hashlib.sha256((r/'game/valve-ally.exe').read_bytes()).hexdigest()!=manifest['sha256']:raise SystemExit('HD build mismatch')
prepare()
for n in ['logs','compatdata']:(r/n).mkdir(exist_ok=True)
env=os.environ.copy();env.update(json.loads((r/'source/runtime-env.json').read_text()))
env.update(STEAM_COMPAT_CLIENT_INSTALL_PATH=str(Path.home()/'.local/share/Steam'),STEAM_COMPAT_DATA_PATH=str(r/'compatdata'),PROTON_LOG='0',WINEDEBUG='-all',WAL_LOG='Z:'+str(r/'logs/payload.log').replace('/',chr(92)))
profile=(r/'dependencias/valve-limit-r.yaml').read_text()
match=re.search(r'^  WAL_PATCHES: "([^"]+)"',profile,re.M)
if not match:raise SystemExit('Missing upstream standalone profile')
env['WAL_PATCHES']=match.group(1)
env['DXVK_LOG_PATH']=str(r/'logs');env['PROTON_LOG_DIR']=str(r/'logs')
env.pop('LD_PRELOAD',None);env.pop('DXVK_HUD',None)
with (r/'logs/controls.log').open('a') as log:
 helper=subprocess.Popen(['python3',str(r/'source/controls.py')],env=env,stdout=log,stderr=subprocess.STDOUT)
 try:
  with (r/'logs/session.log').open('a') as out:
   proton=os.environ.get('VALVE_PROTON',str(Path.home()/'.local/share/Steam/compatibilitytools.d/GE-Proton11-12/proton'))
   subprocess.run([proton,'waitforexitandrun',str(r/'dependencias/wal-loader.exe'),str(r/'dependencias/wal_typex.dll'),str(r/'game/valve-ally.exe')],cwd=r/'game',env=env,stdout=out,stderr=subprocess.STDOUT)
 finally:
  helper.terminate();helper.wait(timeout=8);backup()
