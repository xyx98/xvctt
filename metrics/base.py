from abc import ABC,abstractmethod
class metric(ABC):
    @abstractmethod
    def __init__(self,charset:str):
        pass
    
    @abstractmethod
    def genscript(self,orgscript:str,dstpath:str) -> str:
        pass
    
    @abstractmethod
    def infopath(self,dstpath:str) -> str:
        pass
    
    @abstractmethod
    def getresult(self,infopath:str) -> dict:
        pass