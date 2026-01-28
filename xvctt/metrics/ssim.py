from .base import metric
import re
import csv
from ..utils import MEAN
import statistics

class ssim(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic):
        self.provide=["ssim","ssim-u","ssim-v","ssim-yuv"]
        self.name="ssim"
        self.charset=charset
        self.mean_mode=mean_mode
    
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
        script+=f'last=xvs.ssim2csv({clip},dst,file="{self.infopath(dstpath)}",planes=[0,1,2])\n'
        script+=f'last.set_output()'
        return script
    
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