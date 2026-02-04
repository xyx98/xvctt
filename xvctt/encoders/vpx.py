from .base import encoder_base
import re

class vpx_vp8(encoder_base):
    def __init__(self,encoder_path:str = 'vpxenc',ext:str = 'ivf'):
        super(vpx_vp8,self).__init__(encoder_path,ext)
        self.name="vpx_vp8"
    
    def getbitrate(self,log:str) -> float:
        lastline=log.split("\n")[-2]
        m=re.search(r".+?(\d+)b/s",lastline,re.I)
        if m:
            return float(m.group(1))/1000
        else:
            return -1
        
    def getfps(self, log:str) -> float:
        lastline=log.split("\n")[-2]
        m=re.search(r".+\(([0-9.]+) fps\)",lastline,re.I)
        if m:
            return float(m.group(1))
        else:
            return -1
    
    def gencmd(self,cmd:str,q:int|float|str,output:str) -> str:
        excmd=[]
        if "--codec=" in cmd:
            if "--codec=vp8" not in cmd:
                raise ValueError("vpx_vp8:wrong codec setting in command line.")
        else:
            excmd.append("--codec=vp8")

        if "-p 1" not in cmd or "--passes=1" not in cmd:
            excmd.append("--passes=1")
        
        if "--target-bitrate=" not in cmd:
            excmd.append("--target-bitrate=-1") # for cq rate control mode,it means max bitrate.

        excmdstr=(" "+" ".join(excmd)+" ") if excmd else ""
        return f'{self.encoder_path}{excmdstr}{cmd.format(q=q,output=output)}'
    
class vpx_vp9(encoder_base):
    def __init__(self,encoder_path:str = 'vpxenc',ext:str = 'ivf'):
        super(vpx_vp9,self).__init__(encoder_path,ext)
        self.name="vpx_vp9"
    
    def getbitrate(self,log:str) -> float:
        lastline=log.split("\n")[-2]
        m=re.search(r".+?(\d+)b/s",lastline,re.I)
        if m:
            return float(m.group(1))/1000
        else:
            return -1
        
    def getfps(self, log:str) -> float:
        lastline=log.split("\n")[-2]
        m=re.search(r".+\(([0-9.]+) fps\)",lastline,re.I)
        if m:
            return float(m.group(1))
        else:
            return -1
    
    def gencmd(self,cmd:str,q:int|float|str,output:str) -> str:
        excmd=[]
        if "--codec=" in cmd:
            if "--codec=vp9" not in cmd:
                raise ValueError("vpx_vp9:wrong codec setting in command line.")
        else:
            excmd.append("--codec=vp9")

        if "-p 1" not in cmd or "--passes=1" not in cmd:
            excmd.append("--passes=1")

        excmdstr=(" "+" ".join(excmd)+" ") if excmd else ""
        return f'{self.encoder_path}{excmdstr}{cmd.format(q=q,output=output)}'
    