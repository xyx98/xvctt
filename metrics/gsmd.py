from .base import metric
import re
import csv
from ..utils import MEAN
import statistics

class gmsd(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.average):
        self.provide=["gmsd","gmsd-u","gmsd-v","gmsd-yuv"]
        self.name="gmsd"
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
        script+=f'last=xvs.GMSD2csv({clip},dst,file="{dstpath}_{self.name}.csv",planes=[0,1,2])\n'
        script+=f'last.set_output()'
        return script
    
    def infopath(self,dstpath:str) -> str:
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

        gmsd=[]
        gmsdu=[]
        gmsdv=[]
        gmsdyuv=[]
        for line in data:
            gmsd.append(float(line['Y']))
            gmsdu.append(float(line['U']))
            gmsdv.append(float(line['V']))
            gmsdyuv.append((float(line['Y'])*4+float(line['U'])+float(line['V']))/6)#weighted average 4:1:1 for yuv
        
        return {
            "gmsd":mean(gmsd),
            "gmsd-u":mean(gmsdu),
            "gmsd-v":mean(gmsdv),
            "gmsd-yuv":mean(gmsdyuv)
        }