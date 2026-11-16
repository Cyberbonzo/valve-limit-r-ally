"""English pause menu, rendered locally with SDL2 and the system font."""
import ctypes as C
import os,subprocess
from PIL import Image,ImageDraw,ImageFont

class Menu:
    def __init__(self,sdl):
        self.s=sdl;self.window=None;self.renderer=None;self.texture=None
        self.selected=0;self.last=None;self.infinite=False;self.error=None
        def bind(n,r,a):
            f=getattr(sdl,n);f.restype=r;f.argtypes=a;return f
        self.init=bind('SDL_InitSubSystem',C.c_int,[C.c_uint32])
        self.create=bind('SDL_CreateWindow',C.c_void_p,[C.c_char_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint32])
        self.destroy=bind('SDL_DestroyWindow',None,[C.c_void_p])
        self.raise_window=bind('SDL_RaiseWindow',None,[C.c_void_p])
        self.renderer_create=bind('SDL_CreateRenderer',C.c_void_p,[C.c_void_p,C.c_int,C.c_uint32])
        self.renderer_destroy=bind('SDL_DestroyRenderer',None,[C.c_void_p])
        self.surface=bind('SDL_CreateRGBSurfaceFrom',C.c_void_p,[C.c_void_p,C.c_int,C.c_int,C.c_int,C.c_int,C.c_uint32,C.c_uint32,C.c_uint32,C.c_uint32])
        self.surface_free=bind('SDL_FreeSurface',None,[C.c_void_p])
        self.tex_create=bind('SDL_CreateTextureFromSurface',C.c_void_p,[C.c_void_p,C.c_void_p])
        self.tex_free=bind('SDL_DestroyTexture',None,[C.c_void_p])
        self.copy=bind('SDL_RenderCopy',C.c_int,[C.c_void_p,C.c_void_p,C.c_void_p,C.c_void_p])
        self.present=bind('SDL_RenderPresent',None,[C.c_void_p])
        self.font_path=subprocess.check_output(['fc-match','-f','%{file}','sans'],text=True).strip()

    def show(self):
        if self.window:return
        os.environ.setdefault('SDL_VIDEODRIVER','x11')
        if self.init(0x20)!=0:raise RuntimeError('SDL video initialization failed')
        self.window=self.create(b'Valve Limit R - Pause',0,0,1920,1080,0x8014)
        if not self.window:raise RuntimeError('Pause window creation failed')
        self.renderer=self.renderer_create(self.window,-1,1)
        if not self.renderer:raise RuntimeError('Pause renderer creation failed')
        self.selected=0;self.last=None
        self.raise_window(self.window)

    def hide(self):
        if self.texture:self.tex_free(self.texture);self.texture=None
        if self.renderer:self.renderer_destroy(self.renderer);self.renderer=None
        if self.window:self.destroy(self.window);self.window=None
        self.last=None

    def draw(self):
        if not self.window:return
        state=(self.selected,self.infinite,self.error)
        if state!=self.last:
            im=Image.new('RGBA',(1920,1080),(7,13,23,255));d=ImageDraw.Draw(im)
            def text(x,y,t,size=36,color='#edf4ff'):
                d.text((x,y),t,font=ImageFont.truetype(self.font_path,size),fill=color)
            d.polygon([(1250,0),(1920,0),(1920,1080),(850,1080)],fill='#0c1c2d')
            d.line([(1220,0),(820,1080)],fill='#17415b',width=2)
            text(190,105,'VALVE LIMIT R',27,'#77b9d4')
            text(185,170,'PAUSED',88)
            d.rectangle((190,300,320,308),fill='#34d4f4')
            text(190,345,'Your race is on hold.',30,'#95a8ba')
            for i,label in enumerate(['RESUME','CHEATS: INFINITE BOOST                     '+('ON' if self.infinite else 'OFF')]):
                y=420+i*135;active=self.selected==i
                d.rounded_rectangle((190,y,1730,y+110),radius=14,fill='#14364d' if active else '#101f2d',outline='#34d4f4' if active else '#22364a',width=3)
                text(235,y+32,label,34)
            text(190,690,'Cheat unavailable - see controls log' if self.error else 'Hold A during the race to use nitro. Your cheat preference is saved.',24,'#ffab8c' if self.error else '#5fa7be')
            text(190,765,'LEFT STICK   STEER     RT   GAS / CONFIRM     LT   BRAKE',29,'#95a8ba')
            text(190,820,'A   NITRO / CONFIRM     B   HANDBRAKE     X   VIEW     Y   START',29,'#95a8ba')
            d.line((190,949,1730,949),fill='#22364a',width=2)
            text(190,984,'D-PAD / STICK   SELECT     A   CONFIRM / TOGGLE     B / MENU   RESUME',25,'#99afc2')
            buf=C.create_string_buffer(im.tobytes())
            surface=self.surface(buf,1920,1080,32,1920*4,0xff,0xff00,0xff0000,0xff000000)
            if not surface:raise RuntimeError('Pause surface creation failed')
            texture=self.tex_create(self.renderer,surface);self.surface_free(surface)
            if not texture:raise RuntimeError('Pause texture creation failed')
            if self.texture:self.tex_free(self.texture)
            self.texture=texture;self.last=state
        self.copy(self.renderer,self.texture,None,None);self.present(self.renderer)
