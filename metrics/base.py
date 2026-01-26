from abc import ABC,abstractmethod
from ..utils import MEAN

class metric(ABC):
    @abstractmethod
    def __init__(self,charset:str,mean_mode:MEAN=MEAN.harmonic):
        self.provide=[]
        self.name=""
        self.charset=charset
        self.mean_mode=mean_mode
    
    @abstractmethod
    def genscript(self,orgscript:str,dstpath:str) -> str:
        pass
    
    @abstractmethod
    def infopath(self,dstpath:str) -> str:
        pass
    
    @abstractmethod
    def getresult(self,infopath:str) -> dict:
        pass