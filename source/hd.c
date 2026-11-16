/* Native 16:9 camera and uniformly scaled UI/video for a 1920x1080 backbuffer.
 * Own bridge code; no game resources are embedded.
 */
typedef unsigned int U;
typedef int H;
#define S __attribute__((stdcall))
#define V(o,n) (*(void***)(o))[n]
typedef H(S *DrawIndexed)(void*,U,int,U,U,U,U);
typedef H(S *Transform)(void*,U,void*);
volatile U scaled_draws;
volatile U scaled_video;
volatile U wide_cameras;
volatile float last_projection[16];
float* S perspective(float*out,float fov,float aspect,float nearz,float farz){
 void*d=*(void**)0x581b64,*rt=0;U desc[8]={0};
 if(d && aspect>1.3332f && aspect<1.3335f &&
    ((H(S*)(void*,U,void**))V(d,38))(d,0,&rt)==0 && rt){
  ((H(S*)(void*,U*))V(rt,12))(rt,desc);((H(S*)(void*))V(rt,2))(rt);
  if(desc[6]==1920 && desc[7]==1080){aspect=16.f/9.f;wide_cameras++;}
 }
 float*result=((float*(S*)(float*,float,float,float,float))0x4668b7)(out,fov,aspect,nearz,farz);
 for(U i=0;i<16;i++)last_projection[i]=out[i];
 return result;
}
H S draw_video(void*d,U type,U start,U n){
 U f=0,desc[8]={0};void *rt=0,*vb=0,*ptr=0;U off=0,stride=0;
 ((H(S*)(void*,U*))V(d,90))(d,&f);
 if(f==0x144 && type==5 && n==2 &&
    ((H(S*)(void*,U,void**))V(d,38))(d,0,&rt)==0 && rt){
  ((H(S*)(void*,U*))V(rt,12))(rt,desc);((H(S*)(void*))V(rt,2))(rt);
  if((desc[6]==1440 || desc[6]==1920) && desc[7]==1080 &&
     ((H(S*)(void*,U,void**,U*,U*))V(d,101))(d,0,&vb,&off,&stride)==0 && vb){
   if(stride==28 && ((H(S*)(void*,U,U,void**,U))V(vb,11))(vb,off+start*stride,112,&ptr,0)==0){
    union {U u[28];float f[28];} data;
    for(U i=0;i<28;i++)data.u[i]=((U*)ptr)[i];
    ((H(S*)(void*))V(vb,12))(vb);
    float minx=data.f[0],maxx=minx,miny=data.f[1],maxy=miny;
    for(U i=1;i<4;i++){
     float x=data.f[i*7],y=data.f[i*7+1];
     if(x<minx)minx=x;
     if(x>maxx)maxx=x;
     if(y<miny)miny=y;
     if(y>maxy)maxy=y;
    }
    if(maxx>minx && maxy>miny){
     float sx=desc[6]/(maxx-minx),sy=desc[7]/(maxy-miny),scale=sx<sy?sx:sy;
     float ox=(desc[6]-(maxx-minx)*scale)*.5f-.5f,oy=(desc[7]-(maxy-miny)*scale)*.5f-.5f;
     for(U i=0;i<4;i++){float*v=data.f+i*7;v[0]=(v[0]-minx)*scale+ox;v[1]=(v[1]-miny)*scale+oy;}
    }
    H result=((H(S*)(void*,U,U,const void*,U))V(d,83))(d,type,n,data.u,28);
    ((H(S*)(void*,U,void*,U,U))V(d,100))(d,0,vb,off,stride);
    ((H(S*)(void*))V(vb,2))(vb);scaled_video++;return result;
   }
   ((H(S*)(void*))V(vb,2))(vb);
  }
 }
 return ((H(S*)(void*,U,U,U))V(d,81))(d,type,start,n);
}
H S draw_indexed(void*d,U type,int base,U min,U count,U start,U n){
 U f=0;float original[16],adjusted[16];
 ((H(S*)(void*,U*))V(d,90))(d,&f);
 int scale=0,wide=0;
 if(f==0x142 && ((Transform)V(d,45))(d,3,original)==0 &&
    original[15]==1.f && ((original[0]>.0013888f && original[0]<.001389f) ||
    (wide=(original[0]>.0010416f && original[0]<.0010417f))) &&
    original[5]<-.0018518f && original[5]>-.001852f){
  for(U i=0;i<16;i++)adjusted[i]=original[i];
  adjusted[0]=2.f/640.f;adjusted[5]=-2.f/480.f;
  adjusted[12]=-1.f-1.f/640.f;adjusted[13]=1.f+1.f/480.f;
  if(wide){adjusted[0]*=.75f;adjusted[12]*=.75f;}
  scale=((Transform)V(d,44))(d,3,adjusted)==0;
 }
 H result=((DrawIndexed)V(d,82))(d,type,base,min,count,start,n);
 if(scale){((Transform)V(d,44))(d,3,original);scaled_draws++;}
 return result;
}
