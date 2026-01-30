from .base import metric
import re
import csv
from ..utils import MEAN
import statistics
import textwrap

class ssim(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic,use_vspipe:bool=True):
        self.provide=["ssim","ssim-u","ssim-v","ssim-yuv"]
        self.name="ssim"
        self.charset=charset
        self.mean_mode=mean_mode
        self.use_vspipe=use_vspipe
    
    def genscript(self, orgscript:str,dstpath:str) -> str:
        with open(orgscript,'r',encoding=self.charset) as file:
            script=file.read()
        
        rex=re.compile(r"(.+)\.set_output\(\)")
        
        match=rex.search(script)
        clip=match.group(1)
        
        script=rex.sub("",script)
        script+=f'\nimport xvs\n'
        script+=f'dst=core.lsmas.LWLibavSource(r"{dstpath}",cache=False)\n'
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        script+=f'last=xvs.ssim2csv({clip},dst,file=r"{self.infopath(dstpath)}",planes=[0,1,2])\n'
        script+=f'last.set_output()'
        return script
    
    def run_without_vsipe(self, orgscript:str, dstpath:str) -> bool:
        with open(orgscript,'r',encoding=self.charset) as file:
            script=file.read()
        
        rex=re.compile(r"(.+)\.set_output\(\)")
        
        match=rex.search(script)
        clip=match.group(1)
        
        script=rex.sub("",script)
        script+=f'\nimport xvs\n'
        script+=f'dst=core.lsmas.LWLibavSource(r"{dstpath}",cache=False)\n'
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        #script+=f'last=xvs.ssim2csv({clip},dst,file="{self.infopath(dstpath)}",planes=[0,1,2])\n'
        script+=f'Y=xvs.SSIM({clip},dst,plane=0)\n'
        script+=f'U=xvs.SSIM({clip},dst,plane=1)\n'
        script+=f'V=xvs.SSIM({clip},dst,plane=2)\n\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n,Y,U,V\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                file.write(f"{i},{Y.get_frame(i).props["PlaneSSIM"]},{U.get_frame(i).props["PlaneSSIM"]},{V.get_frame(i).props["PlaneSSIM"]}\n")
                if i % 5 == 0:
                    print(f"\r{i+1}/{length}",end="",flush=True)
            print(f"\r{i+1}/{length}",end="",flush=True)
            print()
            etime=time.time()
            fps=length/(etime-stime)
            print(f"{fps:.02f} fps")
        """.replace("<output>",self.infopath(dstpath)))
        try:
            exec(script)
        except:
            return False
        else:
            return True

    def infopath(self,dstpath:str,fin:bool=False) -> str:
        if fin:
            return f"{dstpath}_{self.name}_fin.csv"
        else:
            return f"{dstpath}_{self.name}.csv"
    
    def getresult(self, infopath:str) -> dict[str,float|int]:
        with open(infopath,"r") as file:
            data=[i for i in csv.DictReader(file)]
            
        if 'U' not in data[0].keys():
            raise RuntimeError("Only support yuv!")

        if self.mean_mode==MEAN.average:
            mean=statistics.fmean
        elif self.mean_mode==MEAN.harmonic:
            mean=statistics.harmonic_mean
        elif self.mean_mode==MEAN.geometric:
            mean=statistics.geometric_mean
        elif self.mean_mode==MEAN.quadratic:
            mean=lambda i: (sum(map(lambda x: x**2),i)/len(i))**0.5

        ssim=[]
        ssimu=[]
        ssimv=[]
        ssimyuv=[]
        for line in data:
            ssim.append(float(line['Y']))
            ssimu.append(float(line['U']))
            ssimv.append(float(line['V']))
            ssimyuv.append((float(line['Y'])*4+float(line['U'])+float(line['V']))/6)#weighted average 4:1:1 for yuv
        
        return {
            "ssim":mean(ssim),
            "ssim-u":mean(ssimu),
            "ssim-v":mean(ssimv),
            "ssim-yuv":mean(ssimyuv)
        }