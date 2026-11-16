"""Build an HD executable locally from the user's supported game revision.

Requires Python 3, GCC with i386 code generation and GNU binutils, no Python
packages. The original executable is never modified. Run on Linux.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,tempfile

ROOT=Path(__file__).resolve().parents[1]
SUPPORTED='f3cfe44a82b16d935d8e6dc46c83cb9893483c2b6018d65e4ed911063061d70e'

def align(v,n):return (v+n-1)//n*n

def build():
 original=ROOT/'game/launcher.exe';data=bytearray(original.read_bytes())
 if hashlib.sha256(data).hexdigest()!=SUPPORTED:raise SystemExit('Unsupported launcher.exe revision')
 pe=struct.unpack_from('<I',data,0x3c)[0]
 if data[pe:pe+4]!=b'PE\0\0':raise SystemExit('Invalid PE')
 coff=pe+4;opt=coff+20
 machine,sections=struct.unpack_from('<HH',data,coff)
 opt_size=struct.unpack_from('<H',data,coff+16)[0]
 if machine!=0x14c or struct.unpack_from('<H',data,opt)[0]!=0x10b:raise SystemExit('Expected PE32 i386')
 base=struct.unpack_from('<I',data,opt+28)[0]
 section_align,file_align=struct.unpack_from('<II',data,opt+32)
 image_size=struct.unpack_from('<I',data,opt+56)[0]
 table=opt+opt_size;va=0x9ad000;rva=va-base
 if image_size!=rva:raise SystemExit('Unexpected section layout')
 def offset(address):
  relative=address-base
  for i in range(sections):
   virtual_size,virtual,raw_size,raw=struct.unpack_from('<4I',data,table+i*40+8)
   if virtual<=relative<virtual+raw_size:return raw+relative-virtual
  raise ValueError('Address outside file')
 with tempfile.TemporaryDirectory(prefix='valve-hd-') as temp:
  tmp=Path(temp);obj=tmp/'hd.o';elf=tmp/'hd.elf';binary=tmp/'hd.bin'
  subprocess.run(['gcc','-m32','-Os','-ffreestanding','-fno-pie','-fno-pic','-fno-stack-protector','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-c',str(ROOT/'source/hd.c'),'-o',str(obj)],check=True)
  subprocess.run(['ld','-m','elf_i386','-T',str(ROOT/'source/hd.ld'),str(obj),'-o',str(elf)],check=True)
  subprocess.run(['objcopy','-O','binary',str(elf),str(binary)],check=True)
  symbols={parts[2]:int(parts[0],16) for line in subprocess.check_output(['nm','-n',str(elf)],text=True).splitlines() if len(parts:=line.split())==3}
  code=binary.read_bytes()
 raw=align(len(data),file_align);raw_size=align(len(code),file_align)
 size=align(max(symbols['_end']-va,len(code)),section_align)
 entry=table+sections*40
 if data[entry:entry+40]!=bytes(40):raise SystemExit('No space for additional section')
 data[entry:entry+40]=struct.pack('<8s6I2HI',b'.ally',size,rva,raw_size,raw,0,0,0,0,0xe0000060)
 struct.pack_into('<H',data,coff+2,sections+1)
 struct.pack_into('<I',data,opt+56,rva+size)
 data.extend(bytes(raw-len(data)));data.extend(code);data.extend(bytes(raw_size-len(code)))
 address=0x46d1a1;at=offset(address)
 if data[at:at+6]!=bytes.fromhex('ff9148010000'):raise SystemExit('Unexpected sprite draw instruction')
 data[at:at+6]=b'\xe8'+struct.pack('<i',symbols['draw_indexed']-address-5)+b'\x90'
 (ROOT/'game/valve-ally.exe').write_bytes(data)
 (ROOT/'docs').mkdir(exist_ok=True)
 report={'original_sha256':SUPPORTED,'sha256':hashlib.sha256(data).hexdigest(),'symbols':symbols,'resolution':[1440,1080]}
 (ROOT/'docs/hd-build.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Built 1440x1080 sprite correction:',report['sha256'])

if __name__=='__main__':build()
