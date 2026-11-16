"""Keep native cabinet storage and bounded automatic backups."""
from pathlib import Path
import hashlib,os,struct
ROOT=Path(__file__).resolve().parents[1]

def valid(data):
 if len(data)!=1332:return False
 decoded=bytes((-v)&255 for v in data)
 for offset,length in [(0,12),(16,16),(36,8),(48,4),(56,1008),(1068,260)]:
  value=0xffffffff
  for byte in decoded[offset:offset+length]:
   value^=byte
   for _ in range(8):value=(value^0xf8 if value&1 else value)>>1
  if ((~value+0x1520)&0xffffffff)!=struct.unpack_from('<I',decoded,offset+length)[0]:return False
 return True
def backup():
 source=ROOT/'game/WindowsLoader';dest=ROOT/'saves/latest'
 if not source.exists():return
 for name in ('expdat','extdat'):
  p=source/name
  if not p.is_file():continue
  rel=p.relative_to(source);data=p.read_bytes()
  if data!=p.read_bytes() or not valid(data):continue
  target=dest/rel
  if target.exists() and target.read_bytes()==data:continue
  target.parent.mkdir(parents=True,exist_ok=True)
  history=ROOT/'saves/history'/rel;history.mkdir(parents=True,exist_ok=True)
  (history/(hashlib.sha256(data).hexdigest()+'.bin')).write_bytes(data)
  versions=sorted(history.glob('*.bin'),key=lambda f:f.stat().st_mtime,reverse=True)
  for f in versions[20:]:f.unlink()
  tmp=target.with_name(target.name+'.tmp');tmp.write_bytes(data);os.replace(tmp,target)
def prepare():
 source=ROOT/'saves/latest';dest=ROOT/'game/WindowsLoader';dest.mkdir(parents=True,exist_ok=True)
 if source.exists():
  for p in source.rglob('*'):
   if p.is_file() and p.name in ('expdat','extdat') and valid(p.read_bytes()):
    target=dest/p.relative_to(source)
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 backup()
