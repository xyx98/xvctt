import re

class encoder_base:
    def __init__(self,encoder_path:str,ext:str,multipass:int):
        self.encoder_path=encoder_path
        self.ext=ext
        self.sep=' '
        self.multipass=multipass
        self.name=""
    
    def getbitrate(self,log:str) -> float:
        m=re.search(r'encoded (\d+) frames.+?([0-9.]+) fps.+?([0-9.]+) kb/s',log,re.I)
        if m:
            return float(m.group(3))
        else:
            return -1
    
    def getfps(self,log:str) -> float:
        m=re.search(r'encoded (\d+) frames.+?([0-9.]+) fps.+?([0-9.]+) kb/s',log,re.I)
        if m:
            return float(m.group(2))
        else:
            return -1
        
    def gencmd(self,cmd:str,q:int|float|str,output:str,p:int=None) -> str:
        return f'{self.encoder_path} {cmd.format(q=q,output=output)}'