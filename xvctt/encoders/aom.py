from .base import encoder_base
import re

class aom_av1(encoder_base):
    def __init__(self,encoder_path:str = 'aomenc',ext:str = 'ivf'):
        super(aom_av1,self).__init__(encoder_path,ext)
        self.name="aom_av1"
    
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
        if "-p 1" not in cmd or "--passes=1" not in cmd:
            return f'{self.encoder_path} --passes=1 {cmd.format(q=q,output=output)}'
        else:
            return f'{self.encoder_path} {cmd.format(q=q,output=output)}'