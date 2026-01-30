from .base import metric
import re
import csv
from ..utils import MEAN
import statistics
import textwrap
from enum import Enum

class vship_ssimulacra2(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.average,use_vspipe:bool=True,numStream:int=1,gpu_id:int=0):
        self.provide=["ssimulacra2"]
        self.name="vship_ssimulacra2"
        self.charset=charset
        self.mean_mode=mean_mode
        self.use_vspipe=use_vspipe
        self.numStream=numStream
        self.gpu_id=gpu_id

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
        script+=f'last=core.vship.SSIMULACRA2({clip},dst,numStream={self.numStream},gpu_id={self.gpu_id})\n'
        script+=f'last=xvs.props2csv(last,["_SSIMULACRA2"],["SSIMULACRA2"],"{self.infopath(dstpath)}")\n'
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
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        script+=f'last=core.vship.SSIMULACRA2({clip},dst,numStream={self.numStream},gpu_id={self.gpu_id})\n\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n\tSSIMULACRA2\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"{i}\t{fprop["_SSIMULACRA2"]}\n")
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

        ssimulacra2=[]

        for line in data:
            ssimulacra2.append(float(line['SSIMULACRA2']))
        
        return {
            "ssimulacra2":mean(ssimulacra2),
        }

class vship_butteraugli(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.average,use_vspipe:bool=True,qnorm:int=2,intensity_multiplier:int|float=203,numStream:int=1,gpu_id:int=0):
        self.provide=["butteraugli_3norm","butteraugli_infnorm"]
        if not qnorm==3:
            self.provide.append(f"butteraugli_{qnorm}norm")
        self.name="vship_butteraugli"
        self.charset=charset
        self.mean_mode=mean_mode
        self.use_vspipe=use_vspipe
        self.qnorm=qnorm
        self.intensity_multiplier=intensity_multiplier
        self.numStream=numStream
        self.gpu_id=gpu_id

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
        script+=f'last=core.vship.BUTTERAUGLI({clip},dst,numStream={self.numStream},gpu_id={self.gpu_id})\n'
        script+=f'last=xvs.props2csv(last,["_BUTTERAUGLI_3Norm","_BUTTERAUGLI_INFNorm","_BUTTERAUGLI_QNorm"],["butteraugli_3norm","butteraugli_infnorm","butteraugli_{self.qnorm}norm"],"{self.infopath(dstpath)}")\n'
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
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        script+=f'last=core.vship.BUTTERAUGLI({clip},dst,numStream={self.numStream},gpu_id={self.gpu_id})\n'

        titlestr=r"n\tbutteraugli_3norm\tbutteraugli_infnorm"#\tbutteraugli_{self.qnorm}norm
        linestr=r'{i}\t{fprop["_BUTTERAUGLI_3Norm"]}\t{fprop["_BUTTERAUGLI_INFNorm"]}'
        if not self.qnorm==3:
            titlestr+=rf"\tbutteraugli_{self.qnorm}norm"
            linestr+=r'\t{fprop["_BUTTERAUGLI_QNorm"]}'
        titlestr+=r"\n"
        linestr+=r"\n"
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("<title>")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"<line>")
                print(f"\r{i+1}/{length}",end="",flush=True)
            print()
            etime=time.time()
            fps=length/(etime-stime)
            print(f"{fps:.02f} fps")
        """
        .replace("<output>",self.infopath(dstpath))
        .replace("<title>",titlestr)
        .replace("<line>",linestr)
        )
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

        butteraugli_3norm=[]
        butteraugli_infnorm=[]
        butteraugli_Qnorm=[]

        for line in data:
            butteraugli_3norm.append(float(line['butteraugli_3norm']))
            butteraugli_infnorm.append(float(line['butteraugli_infnorm']))
            if self.qnorm==3:
                continue
            else:
                butteraugli_Qnorm.append(float(line[f'butteraugli_{self.qnorm}norm']))

        res={
            "butteraugli_3norm":mean(butteraugli_3norm),
            "butteraugli_infnorm":mean(butteraugli_infnorm)
        }

        if not self.qnorm==3:
            res[f"butteraugli_{self.qnorm}norm"]=mean(butteraugli_Qnorm)

        return res
    
class cvvdp_model(Enum):
    standard_4k=0,
    standard_fhd=1,
    standard_hdr_pq=2,
    standard_hdr_hlg=3,
    standard_hdr_dark=4,
    standard_hdr_linear_zoom=5


class vship_cvvdp(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.average,use_vspipe:bool=False,model:cvvdp_model=cvvdp_model.standard_fhd,resizeToDisplay:bool=True,gpu_id:int=0):
        self.provide=[]
        self.name="vship_cvvdp"
        self.charset=charset
        self.mean_mode=mean_mode #not used.
        self.use_vspipe=use_vspipe
        self.model=model
        self.resizeToDisplay=resizeToDisplay
        self.gpu_id=gpu_id

        self.provide.append(f"cvvdp_{self.model.name}")

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
        script+=f'last=core.vship.CVVDP({clip},dst,model_name="{self.model.name}",resizeToDisplay={self.resizeToDisplay},gpu_id={self.gpu_id})\n'
        script+=f'last=xvs.props2csv(last,["_CVVDP"],["{self.provide[0]}"],"{self.infopath(dstpath)}")\n'
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
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        script+=f'last=core.vship.CVVDP({clip},dst,model_name="{self.model.name}",resizeToDisplay={self.resizeToDisplay},gpu_id={self.gpu_id})\n\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n\t<model>\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"{i}\t{fprop["_CVVDP"]}\n")
                print(f"\r{i+1}/{length}",end="",flush=True)
            print()
            etime=time.time()
            fps=length/(etime-stime)
            print(f"{fps:.02f} fps")
        """
        .replace("<output>",self.infopath(dstpath))
        .replace("<model>",self.provide[0])
        )
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

        data_sorted=sorted(data,key=lambda x:int(x["n"]))
        #print(data_sorted)
        return {
            self.provide[0]:data_sorted[-1][self.provide[0]],
        }