import re
from .base import encoder_base

class x265(encoder_base):
    def __init__(self,encoder_path:str = 'x265',ext:str = 'hevc',multipass:int = 0):
        super(x265,self).__init__(encoder_path,ext,multipass)
        self.name="x265"
    
    def getbitrate(self,log:str) -> float:
        return super(x265,self).getbitrate(log)
        
    def getfps(self, log:str) -> float:
        return super(x265,self).getfps(log)
    
    def gencmd(self,cmd:str,q:int|float|str,output:str,p:int=None) -> str:
        p=0 if p is None else p
        if p==0:
            if re.search(r"--y4m",cmd):
                return f'{self.encoder_path} {cmd.format(q=q,output=output)}'
            else:
                return f'{self.encoder_path} --y4m {cmd.format(q=q,output=output)}'
        else:
            if re.search(r"--y4m",cmd):
                return f'{self.encoder_path} --pass {p} {cmd.format(q=q,output=output)}'
            else:
                return f'{self.encoder_path} --y4m --pass {p} {cmd.format(q=q,output=output)}'