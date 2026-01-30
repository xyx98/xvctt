from .base import metric
import re
import csv
from ..utils import MEAN
import statistics
import textwrap

class vszip_ssimulacra2(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic,use_vspipe:bool=True):
        self.provide=["ssimulacra2"]
        self.name="vszip_ssimulacra2"
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
        script+=f'last=core.vszip.SSIMULACRA2({clip},dst)\n'
        script+=f'last=xvs.props2csv(last,["SSIMULACRA2"],["SSIMULACRA2"],r"{self.infopath(dstpath)}")\n'
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
        script+=f'last=core.vszip.SSIMULACRA2({clip},dst)\n\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n\tSSIMULACRA2\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"{i}\t{fprop["SSIMULACRA2"]}\n")
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

class vszip_xpsnr(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic,use_vspipe:bool=True,temporal:bool=True,inf:int|float=100):
        self.provide=["xpsnr","xpsnr-u","xpsnr-v","xpsnr-yuv"]
        self.name="vszip_xpsnr"
        self.charset=charset
        self.mean_mode=mean_mode
        self.use_vspipe=use_vspipe
        self.temporal=temporal
        self.inf=inf 
        #xpsnr's range is 0..inf
        #self.inf>0:when mean calculation,max xpsnr score is self.inf,
        #self.inf<=0:when mean calculation,ingore inf score,if all frames score is inf,set result to abs(self.inf)
    
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
        script+=f'last=core.vszip.XPSNR({clip},dst,temporal={self.temporal},verbose=True)\n'
        script+=f'last=xvs.props2csv(last,["XPSNR_Y","XPSNR_U","XPSNR_V"],["Y","U","V"],r"{self.infopath(dstpath)}")\n'
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
        script+=f'last=core.vszip.XPSNR({clip},dst,temporal={self.temporal},verbose=True)\n'
        script+=textwrap.dedent(
        r"""        
        import time
        with open(r"<output>","w") as file:
            file.write("n\tY\tU\tV\n")
            length=len(src)
            stime=time.time()
            for i in range(length):
                fprop=last.get_frame(i).props
                file.write(f"{i}\t{fprop["XPSNR_Y"]}\t{fprop["XPSNR_U"]}\t{fprop["XPSNR_V"]}\n")
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

        xpsnr=[]
        xpsnru=[]
        xpsnrv=[]
        xpsnryuv=[]
        if self.inf>0:
            for line in data:
                Y,U,V=line['Y'],line['U'],line['V']
                Y=self.inf if Y.strip()=="inf" else min(float(Y),self.inf)
                xpsnr.append(Y)
                U=self.inf if U.strip()=="inf" else min(float(U),self.inf)                
                xpsnru.append(U)
                V=self.inf if V.strip()=="inf" else min(float(V),self.inf)                    
                xpsnrv.append(V)
                xpsnryuv.append((Y*4+U+V)/6)#weighted average 4:1:1 for yuv
        else:
            for line in data:
                Y,U,V=line['Y'],line['U'],line['V']
                YUV_NUM=0
                YUV_DEN=0
                if Y.strip()!="inf":
                    xpsnr.append(float(Y))
                    YUV_NUM+=4*float(Y)
                    YUV_DEN+=4
                if U.strip()!="inf":
                    xpsnr.append(float(U))
                    YUV_NUM+=float(U)
                    YUV_DEN+=1
                if V.strip()!="inf":
                    xpsnr.append(float(V))
                    YUV_NUM+=float(V)
                    YUV_DEN+=1
                if YUV_DEN>0:
                    xpsnryuv.append(YUV_NUM/YUV_DEN)
                
        return {
            "xpsnr":mean(xpsnr) if len(xpsnr)>0 else abs(self.inf),
            "xpsnr-u":mean(xpsnru) if len(xpsnru)>0 else abs(self.inf),
            "xpsnr-v":mean(xpsnrv) if len(xpsnrv)>0 else abs(self.inf),
            "xpsnr-yuv":mean(xpsnryuv) if len(xpsnryuv)>0 else abs(self.inf)
        }