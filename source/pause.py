"""Suspend this game and exclude paused time from its imported clocks."""
import os,signal,struct,time
from pathlib import Path
def u32(value):return struct.pack('<I',value)
class Pause:
    def __init__(self):self.stopped={}
    def apply(self,pids,value):
        if value:
            for pid in pids:
                if pid in self.stopped:continue
                fd=os.open(f'/proc/{pid}/mem',os.O_RDWR)
                try:
                    if os.pread(fd,6,0x40b2b3)!=bytes.fromhex('ff1530d34b00'):raise RuntimeError('Unsupported game timer')
                    freq=10_000_000  # Wine/Proton QueryPerformanceFrequency
                    if not 1000<=freq<=10**10:raise RuntimeError('Invalid clock frequency')
                    os.kill(pid,signal.SIGSTOP)
                    for _ in range(100):
                        if '\nState:\tT' in Path(f'/proc/{pid}/status').read_text():break
                        time.sleep(.001)
                    else:raise RuntimeError('Game did not suspend')
                    cave=0x4bc180;block=os.pread(fd,192,cave)
                    if block[:8]==b'VLRPAU01':
                        for slot,entry in [(0x4bd13c,48),(0x4bd1c0,112),(0x4bd330,144)]:
                            if os.pread(fd,4,slot)!=u32(cave+entry):raise RuntimeError('Clock hook changed')
                    elif block==bytes(192):
                        data=bytearray(192);data[:8]=b'VLRPAU01'
                        for slot,offset in [(0x4bd13c,24),(0x4bd1c0,28),(0x4bd330,32)]:data[offset:offset+4]=os.pread(fd,4,slot)
                        code=bytes.fromhex('568B74240856FF15')+u32(cave+24)
                        code+=bytes.fromhex('8B0E2B0D')+u32(cave+8)
                        code+=bytes.fromhex('8B56041B15')+u32(cave+12)
                        code+=bytes.fromhex('890E8956045EC20400')
                        data[48:48+len(code)]=code
                        for entry,original in [(112,28),(144,32)]:
                            code=bytes.fromhex('FF15')+u32(cave+original)+bytes.fromhex('2B05')+u32(cave+16)+b'\xc3'
                            data[entry:entry+len(code)]=code
                        os.pwrite(fd,data,cave)
                        for slot,entry in [(0x4bd13c,48),(0x4bd1c0,112),(0x4bd330,144)]:os.pwrite(fd,u32(cave+entry),slot)
                    else:raise RuntimeError('Clock storage is not unused')
                    self.stopped[pid]=(fd,cave,freq,time.monotonic_ns())
                except BaseException:
                    try:os.kill(pid,signal.SIGCONT)
                    finally:os.close(fd)
                    raise
        else:
            for pid,(fd,cave,freq,started) in list(self.stopped.items()):
                try:
                    elapsed=time.monotonic_ns()-started
                    old=struct.unpack('<Q',os.pread(fd,8,cave+8))[0]
                    os.pwrite(fd,struct.pack('<Q',old+round(elapsed*freq/1e9)),cave+8)
                    old=struct.unpack('<I',os.pread(fd,4,cave+16))[0]
                    os.pwrite(fd,u32((old+round(elapsed/1e6))&0xffffffff),cave+16)
                    print('Pause excluded %.3f seconds'%(elapsed/1e9),flush=True)
                finally:
                    try:os.kill(pid,signal.SIGCONT)
                    except ProcessLookupError:pass
                    os.close(fd);del self.stopped[pid]
