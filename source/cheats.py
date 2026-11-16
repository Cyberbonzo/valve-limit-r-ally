"""Optional local-player nitro refill for the supported game revision."""
import json,os,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class Cheats:
    def __init__(self):
        self.path=ROOT/'settings.json';self.enabled=False;self.error=None
        self.pid=None;self.fd=None;self.refills=0
        try:self.enabled=json.loads(self.path.read_text()).get('infinite_boost') is True
        except (OSError,ValueError):pass

    def toggle(self):
        value=not self.enabled
        temp=self.path.with_suffix('.tmp')
        temp.write_text(json.dumps({'infinite_boost':value},indent=2)+'\n')
        temp.replace(self.path);self.enabled=value

    def close(self):
        if self.fd is not None:os.close(self.fd)
        self.fd=None;self.pid=None

    def update(self,pids):
        if self.pid not in pids:self.close()
        if not self.enabled or not pids:return
        try:
            if self.fd is None:
                fd=os.open(f'/proc/{pids[0]}/mem',os.O_RDWR)
                # Validate the original local-player nitro charge decrement.
                if os.pread(fd,7,0x45282c)!=bytes.fromhex('8080f4040000ff'):
                    os.close(fd);raise RuntimeError('Unsupported nitro routine')
                self.fd=fd;self.pid=pids[0]
            def u32(a):return struct.unpack('<I',os.pread(self.fd,4,a))[0]
            if u32(0x5824f0)!=35:return  # Active race only.
            car=u32(0x4ef4f8)
            if not 0x400000<=car<=0x7ffff000 or u32(car)!=0:return
            # One charge is enough: native activation, effects and duration remain intact.
            if os.pread(self.fd,1,car+0x4f4)==b'\0':
                os.pwrite(self.fd,b'\1',car+0x4f4);self.refills+=1
            self.error=None
        except (OSError,ValueError,struct.error,RuntimeError) as exc:
            message=str(exc)
            if self.error!=message:print('Cheat unavailable:',message,flush=True)
            self.error=message;self.close()
