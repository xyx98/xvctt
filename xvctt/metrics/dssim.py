from .base import metric
import re
import csv
from ..utils import MEAN
import statistics
import textwrap

class dssim(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.average,use_vspipe=True):
        self.provide=["dssim","ssim"]
        self.name="dssim"
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
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format=vs.RGB24,matrix_in_s="709")\n'
        script+=f'{clip}=core.resize.Spline36({clip},format=vs.RGB24,matrix_in_s="709")\n'
        script+=f'last=core.dssim.dssim({clip},dst)\n'
        script+=f'last=xvs.props2csv(last,["dssim_score","dssim_ssim"],["dssim","ssim"],"{self.infopath(dstpath)}")\n'
        script+=f'last.set_output()'
        return script

    def run_without_vsipe(self, orgscript:str, dstpath:str):
        with open(orgscript,'r',encoding=self.charset) as file:
            script=file.read()
        
        rex=re.compile(r"(.+)\.set_output\(\)")
        
        match=rex.search(script)
        clip=match.group(1)
        
        script=rex.sub("",script)
        script+=f'\nimport xvs\n'
        script+=f'dst=core.lsmas.LWLibavSource(r"{dstpath}",cache=False)\n'
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format=vs.RGB24,matrix_in_s="709")\n'
        script+=f'{clip}=core.resize.Spline36({clip},format=vs.RGB24,matrix_in_s="709")\n'
        script+=f'last=core.dssim.dssim({clip},dst)\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n\tdssim\tssim\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"{i}\t{fprop["dssim_score"]}\t{fprop["dssim_ssim"]}\n")
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
        return True

    def infopath(self,dstpath:str,fin:bool=False) -> str:
        if fin:
            return f"{dstpath}_{self.name}_fin.csv"
        else:
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

        dssim=[]
        ssim=[]

        for line in data:
            dssim.append(float(line['dssim']))
            ssim.append(float(line['ssim']))
        
        return {
            "dssim":mean(dssim),
            "ssim":mean(ssim),
        }