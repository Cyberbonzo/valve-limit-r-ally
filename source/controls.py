"""ROG Ally controls and pause, using the open WAL TCP input protocol."""
import ctypes as C
import os,signal,struct,time,json,socket,subprocess
from pathlib import Path
from pause import Pause
from pause_menu import Menu
from progress import backup
from cheats import Cheats

pause_manager=Pause()

ROOT=Path(__file__).resolve().parents[1]

TEST=ROOT/'logs/test-input.json'
os.environ['SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS']='1'
os.environ['SDL_GAMECONTROLLER_ALLOW_STEAM_VIRTUAL_GAMEPAD']='0'
os.environ.pop('SDL_GAMECONTROLLER_IGNORE_DEVICES',None)
steam_id=os.environ.get('SteamAppId',os.environ.get('SteamGameId',''))
if steam_id.isdigit():
    app_id=int(steam_id)
    if app_id>0xffffffff:app_id>>=32
    os.environ['SDL_VIDEO_X11_WMCLASS']='steam_app_'+str(app_id)
for key in ('SteamAppId','SteamGameId','SteamVirtualGamepadInfo','SteamOverlayGameId'):
    os.environ.pop(key,None)
os.environ['SDL_JOYSTICK_HIDAPI']='0'
s=C.CDLL('libSDL2-2.0.so.0')
def bind(lib,n,r,a):
    f=getattr(lib,n);f.restype=r;f.argtypes=a;return f
bind(s,'SDL_Init',C.c_int,[C.c_uint32])(0x2200)
op=bind(s,'SDL_GameControllerOpen',C.c_void_p,[C.c_int])
axis=bind(s,'SDL_GameControllerGetAxis',C.c_int16,[C.c_void_p,C.c_int])
button=bind(s,'SDL_GameControllerGetButton',C.c_uint8,[C.c_void_p,C.c_int])
attached=bind(s,'SDL_GameControllerGetAttached',C.c_int,[C.c_void_p])
close=bind(s,'SDL_GameControllerClose',None,[C.c_void_p])
name=bind(s,'SDL_GameControllerName',C.c_char_p,[C.c_void_p])
running=True
def stop(*_):
    global running
    running=False
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
def game_pids():
    found=[]
    for p in Path('/proc').glob('[0-9]*'):
        try:
            command=(p/'cmdline').read_bytes().decode(errors='replace').replace('\\','/')
            if (p/'comm').read_text().strip() in ('launcher.exe','valve-ally.exe') and '/'+ROOT.name+'/game/' in command:
                found.append(int(p.name))
        except (OSError,ValueError):pass
    return found
def set_pause(value):
    if value:
        try:
            pause_manager.apply(game_pids(),True)
            menu.show();menu.draw()
        except BaseException:
            menu.hide();pause_manager.apply([],False);raise
    else:
        menu.hide();pause_manager.apply([],False)

def packet(kind,payload):return struct.pack('<BBH',kind,0,len(payload))+payload
server=socket.socket();server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind(('127.0.0.1',33707));server.listen(1);server.setblocking(False)
pad=None;client=None;old=set();paused=False;last_status=0
menu=Menu(s);cheats=Cheats();menu.infinite=cheats.enabled
last_menu=0;last_pids=0;pids=[];old_direction=0
started=time.monotonic();last_backup=0
try:
 while running:
    now=time.monotonic()
    if client is None:
        try:
            client,_=server.accept();client.setblocking(False)
            client.sendall(packet(1,struct.pack('<H',1)+b'ValveLimitR-Ally'))
            print('Game connected',flush=True)
        except BlockingIOError:pass
    s.SDL_PumpEvents();s.SDL_GameControllerUpdate()
    if pad and not attached(pad):close(pad);pad=None
    if not pad:
        for i in range(s.SDL_NumJoysticks()):
            if s.SDL_IsGameController(i):
                candidate=op(i)
                if candidate:
                    n=name(candidate).decode()
                    if 'Elite' in n or 'ROG' in n:pad=candidate;break
                    close(candidate)
    pressed={i for i in range(15) if pad and button(pad,i)}
    wheel=axis(pad,0)/32767 if pad else 0
    wheel=0 if abs(wheel)<.12 else (abs(wheel)-.12)/.88*(1 if wheel>0 else -1)
    gas=max(0,axis(pad,5)/32767) if pad else 0
    brake=max(0,axis(pad,4)/32767) if pad else 0
    s.SDL_FlushEvents(0,0xffff)
    t={}
    if TEST.exists():
        try:
            if time.time()-TEST.stat().st_mtime<10:
                t=json.loads(TEST.read_text())
                pressed=set(t.get('buttons',[]));wheel=t.get('wheel',0);gas=t.get('gas',0);brake=t.get('brake',0)
        except (OSError,ValueError):pass
    edge=pressed-old
    vertical=axis(pad,1)/32767 if pad else 0
    if t:vertical=t.get('menu_y',0)
    direction=-1 if 11 in pressed or vertical<-.6 else 1 if 12 in pressed or vertical>.6 else 0
    was_paused=paused
    if paused:
        if direction and direction!=old_direction:menu.selected=(menu.selected+direction)%2
        if menu.selected==1 and (0 in edge or 13 in edge or 14 in edge):
            cheats.toggle();menu.infinite=cheats.enabled
    if 6 in edge or (paused and (1 in edge or (0 in edge and menu.selected==0))):
        paused=not paused;set_pause(paused);print('Pause:',paused,flush=True)
    if now-last_pids>1:pids=game_pids();last_pids=now
    cheats.update(pids)
    menu.error=cheats.error
    if paused and now-last_menu>.1:
        menu.draw();last_menu=now
    bits=0
    for physical,virtual in [(0,4),(0,12),(1,6),(2,5),(3,12),(4,13),(9,8),(10,7)]:
        if physical in pressed:bits|=1<<virtual
    bits|=int(t.get('bits',0))
    if paused or was_paused:bits=0;wheel=gas=brake=0
    payload=struct.pack('<I6h',bits,round(max(-1,min(1,wheel))*32767),0,0,0,round(gas*32767),round(brake*32767))+bytes(48)
    if client and not paused:
        try:
            try:
                incoming=client.recv(65536)
                if not incoming:raise ConnectionError('Closed')
            except BlockingIOError:pass
            client.sendall(packet(2,payload))
        except BlockingIOError:pass
        except OSError:client.close();client=None
    if now-last_status>1:
        last_status=now
        (ROOT/'logs/controls-status.json').write_text(json.dumps({'controller':name(pad).decode() if pad else None,'paused':paused,'menu_selected':menu.selected,'infinite_boost':cheats.enabled,'boost_refills':cheats.refills,'cheat_error':cheats.error,'connected':client is not None,'buttons':sorted(pressed),'wheel':wheel,'gas':gas,'brake':brake}))
    if now-last_backup>10:
        backup();last_backup=now
    old=pressed;old_direction=direction;time.sleep(.008)
finally:
 cheats.close()
 if paused:set_pause(False)

 menu.hide()
 if client:client.close()
 server.close()
 if pad:close(pad)
 s.SDL_Quit()
