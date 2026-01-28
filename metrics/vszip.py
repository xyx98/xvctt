from .base import metric
import re
import csv
from ..utils import MEAN
import statistics

class vszip_ssimulacra2(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic):
        self.provide=["ssimulacra2"]
        self.name="vszip_ssimulacra2"
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
        script+=f'last=core.vszip.SSIMULACRA2({clip},dst)\n'
        script+=f'last=xvs.props2csv(last,["SSIMULACRA2"],["SSIMULACRA2"],"{self.infopath(dstpath)}")\n'
        script+=f'last.set_output()'
        return script
    
    def infopath(self,dstpath:str) -> str:
        return f"{dstpath}_{self.name}.csv"
    
    def getresult(self, infopath:str) -> dict[str,float|int]:
        with open(infopath,"r") as file:
            data=[i for i in csv.DictReader(file,delimiter="\t")]

        if self.mean_mode==MEAN.average:
            mean=statistics.fmean
        elif self.mean_mode==MEAN.harmonic:
            mean=statistics.harmonic_mean
        elif self.mean_mode==MEAN.geometric:
            mean=statistics.geometric_mean
        elif self.mean_mode==MEAN.quadratic:
            mean=lambda i: (sum(map(lambda x: x**2),i)/len(i))**0.5

        ssimulacra2=[]

        for line in data:
            ssimulacra2.append(float(line['SSIMULACRA2']))
        
        return {
            "ssimulacra2":mean(ssimulacra2),
        }