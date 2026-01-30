from .utils import applybackspace,calcbitrate,calcfps,get_video_info_by_vs
from .encoders.base import encoder_base
from .metrics.base import metric

import os
import sys
import subprocess
import time

class atomTest:
    def __init__(self,vspipe:str,vpypath:str,cmd:str,q:int|float|str,workdir:str,output:str,encoder:encoder_base,metrics:metric|list[metric]):
        self.vpypath=vpypath
        self.vspipe=vspipe
        self.cmd=cmd
        self.q=q
        self.workdir=workdir
        self.output=output
        self.encoder=encoder
        self.metrics=metrics if isinstance(metrics,list) else [metrics]
        self.time=-1
        self.succuss=0 #0:not run yet 1:succuss -1:fail
        os.makedirs(self.workdir,exist_ok=True)
    
    def encode(self) -> bool:
        if self.encoder.multipass<2:
            output=os.path.join(self.workdir,self.output)
            cmdline=f'{self.vspipe} -c y4m {self.vpypath} -|{self.encoder.gencmd(self.cmd,self.q,output+'.'+self.encoder.ext)}'
            #print(cmdline)
            t=time.time()
            sp=subprocess.Popen(cmdline,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            logtext=""
            while(True):
                stats=sp.poll()
                if stats is not None:
                    self.time=time.time()-t
                    info=sp.stderr.read()
                    if isinstance(info,bytes):
                        info=info.decode("utf-8")
                    logtext+=info
                    sys.stderr.write(info)
                    sys.stderr.flush()

                    with open(f"{output}.log","w") as file:
                        file.write(applybackspace(logtext))
                    return stats==0
                else:
                    info=sp.stderr.read(1)
                    if isinstance(info,bytes):
                        info=info.decode("utf-8")
                    logtext+=info
                    sys.stderr.write(info)
                    sys.stderr.flush()

        return False


    def run(self) -> bool:
        output=os.path.join(self.workdir,self.output)
        if not os.path.exists(f"{output}_fin.{self.encoder.ext}"):
            if os.path.exists(f"{output}.{self.encoder.ext}"):
                os.remove(f"{output}.{self.encoder.ext}")
            enc=self.encode()
            if not enc:
                self.succuss=-1
                return False
            else:
                os.rename(f"{output}.{self.encoder.ext}",f"{output}_fin.{self.encoder.ext}")

        returncode=0
        for m in self.metrics:
            if os.path.exists(m.infopath(f"{output}_fin.{self.encoder.ext}",fin=True)): #simple check
                continue

            if m.use_vspipe:
                script=m.genscript(self.vpypath,f"{output}_fin.{self.encoder.ext}")
                with open (".metric.vpy",'w',encoding=m.charset) as file:
                    file.write(script)
                    
                sp=subprocess.run(f'{self.vspipe} -p ".metric.vpy" .',shell=True)
                if sp.returncode==0:
                    os.rename(
                        m.infopath(f"{output}_fin.{self.encoder.ext}",fin=False),
                        m.infopath(f"{output}_fin.{self.encoder.ext}",fin=True)
                    )

                returncode=returncode or sp.returncode
                os.remove(".metric.vpy")
            else:
                success=m.run_without_vsipe(self.vpypath,f"{output}_fin.{self.encoder.ext}")
                if not success:
                    returncode = 1
                else:
                    os.rename(
                        m.infopath(f"{output}_fin.{self.encoder.ext}",fin=False),
                        m.infopath(f"{output}_fin.{self.encoder.ext}",fin=True)
                    )
        if returncode==0:
            self.succuss=1
            return True
        else:
            self.succuss=-1
            return False
    
    def collect_result(self) -> dict[str,int|float]:
        output=os.path.join(self.workdir,self.output)
        filepath=f"{output}_fin.{self.encoder.ext}"
        with open(f"{output}.log","r") as file:
            log=file.read()
        
        fps=self.encoder.getfps(log)
        bitrate=self.encoder.getbitrate(log)
        
        if fps < 0 or bitrate < 0:
            info=get_video_info_by_vs(filepath)
            frames=info["frames"]
            duration=info["duration"]
            if fps < 0:
                fps= -1 if (self.time < 0 or frames < 0) else calcfps(frames,self.time)
            
            if bitrate < 0:
                bitrate= -1 if duration < 0 else calcbitrate(filepath,duration*1000)
                
        res={"fps":fps,"bitrate":bitrate,"metrics":{}}
        
        for m in self.metrics:
            res["metrics"][m.name]=m.getresult(m.infopath(filepath,fin=True))
            
        return res
    
        