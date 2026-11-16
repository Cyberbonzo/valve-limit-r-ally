/* D3DX sprite projection correction for a 4:3 1440x1080 backbuffer.
 * Own bridge code; no game resources are embedded.
 */
typedef unsigned int U;
typedef int H;
#define S __attribute__((stdcall))
#define V(o,n) (*(void***)(o))[n]
typedef H(S *DrawIndexed)(void*,U,int,U,U,U,U);
typedef H(S *Transform)(void*,U,void*);
volatile U scaled_draws;
H S draw_indexed(void*d,U type,int base,U min,U count,U start,U n){
 U f=0;float original[16],adjusted[16];
 ((H(S*)(void*,U*))V(d,90))(d,&f);
 int scale=0;
 if(f==0x142 && ((Transform)V(d,45))(d,3,original)==0 &&
    original[15]==1.f && original[0]>.0013888f && original[0]<.001389f &&
    original[5]<-.0018518f && original[5]>-.001852f){
  for(U i=0;i<16;i++)adjusted[i]=original[i];
  adjusted[0]=2.f/640.f;adjusted[5]=-2.f/480.f;
  adjusted[12]=-1.f-1.f/640.f;adjusted[13]=1.f+1.f/480.f;
  scale=((Transform)V(d,44))(d,3,adjusted)==0;
 }
 H result=((DrawIndexed)V(d,82))(d,type,base,min,count,start,n);
 if(scale){((Transform)V(d,44))(d,3,original);scaled_draws++;}
 return result;
}
