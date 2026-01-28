from .base import encoder_base
import re

class svt_av1(encoder_base):
    def __init__(self,encoder_path:str = 'SvtAv1EncApp',ext:str = 'ivf'):
        super(svt_av1,self).__init__(encoder_path,ext)
        self.name="svt_av1"
    
    def getbitrate(self,log:str) -> float:
        m=re.search(r".+?([0-9.]+) kbps",log,re.I)
        if m:
            return float(m.group(1))
        else:
            return -1
        
    def getfps(self, log:str) -> float:
        m=re.search(r"Average Speed:.+?([0-9.]+).*fps",log,re.I)
        if m:
            return float(m.group(1))
        else:
            return -1
    
    def gencmd(self,cmd:str,q:int|float|str,output:str) -> str:
        return f'{self.encoder_path} {cmd.format(q=q,output=output)}'