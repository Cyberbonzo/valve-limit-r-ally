/* Render intermediate scene poses while retaining the original game update rate. */
typedef unsigned int U;
#define T __attribute__((thiscall))
#define MEM(a) (*(volatile U*)(a))
typedef struct {U key,mesh,draw,epoch;float previous[6],current[6];} Pose;
static Pose poses[2048];
static Pose* active[1024];
static Pose characters[32];
static Pose* active_characters[32];
typedef struct {U key,epoch;float previous[10],current[10];} CarPose;
static CarPose cars[64];
static CarPose* active_cars[64];
static float camera_previous[6];
static U camera_valid,epoch;
volatile U fps_enabled=1;
volatile U render_frames,intermediate_frames,logic_frames,interpolated_objects;
volatile U render_phase;
volatile U interpolated_cars;
volatile U interpolated_characters;
volatile float camera_midpoint[6],camera_endpoint[6];

static float delta(float x,float wrap){
 if(x>wrap*.5f)x-=wrap;
 if(x< -wrap*.5f)x+=wrap;
 return x;
}
static void copy6(float*a,const float*b){for(U i=0;i<6;i++)a[i]=b[i];}
static int reasonable(const float*p){
 for(U i=0;i<6;i++)if(!(p[i]>-1000000.f && p[i]<1000000.f))return 0;
 return 1;
}

/* Native render also services movie/overlay animations. Do that once per tick. */
void video_tick(void){if(render_phase!=1)((void(*)(void))0x412320)();}

/* Read the existing crash-animation pose without advancing its frame or physics. */
int car_animation(U car,float*position,float*rotation){
 if(render_phase!=1)return ((int(*)(U,float*,float*))0x42fcb0)(car,position,rotation);
 unsigned char state=*(unsigned char*)(car+0x494);
 U table=MEM(0x586980);
 if(*(unsigned char*)0x5824a1!=12 || !state || !table)return 0;
 int kind=*(signed char*)(car+0x495);
 U offset=*(unsigned short*)(table+(kind==0?0:kind==1?4:kind==2?8:10));
 U frame=state==1?0:MEM(car+0x490),length=MEM(table+(offset/4)*4);
 if(frame>=length)return 0;
 const float*pose=(const float*)(table+offset+4+frame*24);
 for(U i=0;i<3;i++){position[i]=pose[i];rotation[i]=pose[i+3];}
 return 1;
}

void T render_60(void* graphics){
 logic_frames++;
 U state=MEM(0x5824f0),race_phase=MEM(0x5825c4);
 if(!fps_enabled || state!=35 || race_phase!=2){
  camera_valid=0;
  ((void(T*)(void*))0x406710)(graphics);render_frames++;return;
 }
 epoch++;
 float*camera=(float*)0x4e61fc;float current[6];copy6(current,camera);
 U count=0,car_count=0,character_count=0,visited=0,node=MEM(0x506ac4);
 while(node && visited++<4096){
  U next=MEM(node+0x14),draw=MEM(node+0x68),mesh=MEM(node+0x1c);
  /* Animated characters follow the camera in world space. Their root must
     follow the same interpolation even when the regular mesh cache is full. */
  if(draw==0x458120 && character_count<32){
   float*values=(float*)(node+0x3c);U slot=(node>>4)&31;
   if(reasonable(values))for(U tries=0;tries<32;tries++,slot=(slot+1)&31){
    Pose*p=characters+slot;
    if(p->key!=node && p->epoch==epoch)continue;
    U instance=MEM(node+0x10);
    int valid=p->key==node && p->mesh==mesh && p->draw==instance && p->epoch==epoch-1 && camera_valid;
    copy6(p->current,values);
    if(valid){
     for(U i=0;i<6;i++){float d=values[i]-p->previous[i];if(i>=3)d=delta(d,360.f);values[i]=p->previous[i]+d*.5f;}
     interpolated_characters++;
    }
    p->key=node;p->mesh=mesh;p->draw=instance;p->epoch=epoch;
    active_characters[character_count++]=p;break;
   }
  }
  if(draw==0x42d040 && car_count<64){
   U car=MEM(node+0x80),slot=(car>>4)&63;
   if(car){
    for(U tries=0;tries<64;tries++,slot=(slot+1)&63){
     CarPose*p=cars+slot;
     if(p->epoch==epoch){if(p->key==car)break;else continue;}
     float*values=(float*)(car+0x180);
     int valid=p->key==car && p->epoch==epoch-1 && camera_valid;
     float distance=0;
     for(U i=0;i<10;i++){p->current[i]=values[i];if(i<4){float d=values[i]-p->previous[i];distance+=d*d;}}
     if(valid && distance<10000.f){
      for(U i=0;i<10;i++){float d=values[i]-p->previous[i];if(i>=4)d=delta(d,6.28318530718f);values[i]=p->previous[i]+d*.5f;}
      interpolated_cars++;
     }
     p->key=car;p->epoch=epoch;active_cars[car_count++]=p;break;
    }
   }
  }
  /* Persistent standard mesh nodes have the same position/rotation layout. */
  if(count<1024 && (draw==0x4039f0 || draw==0x403ae0 || draw==0x403b70 || draw==0x403c40)){
   float*values=(float*)(node+0x3c);
   if(reasonable(values)){
    U slot=(node>>4)&2047;
    for(U tries=0;tries<16;tries++,slot=(slot+1)&2047){
     Pose*p=poses+slot;
     if(p->key!=node && p->epoch==epoch)continue;
     int valid=p->key==node && p->mesh==mesh && p->draw==draw && p->epoch==epoch-1 && camera_valid;
     copy6(p->current,values);
     if(valid){
      for(U i=0;i<6;i++){
       float d=values[i]-p->previous[i];if(i>=3)d=delta(d,360.f);
       values[i]=p->previous[i]+d*.5f;
      }
      interpolated_objects++;
     }
     p->key=node;p->mesh=mesh;p->draw=draw;p->epoch=epoch;
     active[count++]=p;break;
    }
   }
  }
  if(next==node)break;node=next;
 }
 if(camera_valid && reasonable(current)){
  float distance=0.f;for(U i=0;i<3;i++){float d=current[i]-camera_previous[i];distance+=d*d;}
  if(distance<10000.f){
   for(U i=0;i<6;i++){
    float d=current[i]-camera_previous[i];if(i>=3)d=delta(d,6.28318530718f);
    camera[i]=camera_previous[i]+d*.5f;
   }
  }
 }
 for(U i=0;i<6;i++){camera_midpoint[i]=camera[i];camera_endpoint[i]=current[i];}
 U sprite_count=MEM(0x575764);
 render_phase=1;
 ((void(T*)(void*))0x406710)(graphics);
 render_frames++;intermediate_frames++;
 copy6(camera,current);copy6(camera_previous,current);camera_valid=1;
 for(U j=0;j<count;j++){
  Pose*p=active[j];copy6((float*)(p->key+0x3c),p->current);copy6(p->previous,p->current);
 }
 for(U j=0;j<character_count;j++){
  Pose*p=active_characters[j];copy6((float*)(p->key+0x3c),p->current);copy6(p->previous,p->current);
 }
 for(U j=0;j<car_count;j++){
  CarPose*p=active_cars[j];float*values=(float*)(p->key+0x180);
  for(U i=0;i<10;i++){values[i]=p->current[i];p->previous[i]=p->current[i];}
 }
 MEM(0x575764)=sprite_count;
 render_phase=2;
 ((void(T*)(void*))0x406710)(graphics);render_frames++;
 render_phase=0;
}
