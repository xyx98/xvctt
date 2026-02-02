import re
from .base import encoder_base

class rav1e(encoder_base):
    def __init__(self,encoder_path:str = 'rav1e',ext:str = 'ivf'):
        super(rav1e,self).__init__(encoder_path,ext)
        self.name="rav1e"
    
    def getbitrate(self,log:str) -> float:
        m=re.search(r'>  encoded (\d+) frames.+?([0-9.]+) fps.+?([0-9.]+) kb/s',log,re.I)
        if m:
            return float(m.group(3))
        else:
            return -1
    
    def getfps(self,log:str) -> float:
        m=re.search(r'>  encoded (\d+) frames.+?([0-9.]+) fps.+?([0-9.]+) kb/s',log,re.I)
        if m:
            return float(m.group(2))
        else:
            return -1
    
    def gencmd(self,cmd:str,q:int|float|str,output:str) -> str:
        return f'{self.encoder_path} {cmd.format(q=q,output=output)}'

