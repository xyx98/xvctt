from .atomTest import atomTest
from .encoders.base import encoder_base
from .metrics.base import metric
from .utils import loadjson,add_fmtc_bitdepth_for_vpy
import os
import json

class singleTest:
    def __init__(self,vspipe:str,vpypath:str,cmd:str,qlist:list[int|float|str],workdir:str,output:str,encoder:encoder_base,metrics:metric|list[metric],name:str|None = None,convertbits:int=-1,charset:str="utf-8"):
        self.vpypath=vpypath
        self.vspipe=vspipe
        self.cmd=cmd
        self.qlist=qlist
        self.workdir=workdir
        self.output=output
        self.encoder=encoder
        self.metrics=metrics if isinstance(metrics,list) else [metrics]
        self.time=-1
        self.name = self.output if name is None else name
        self.convertbits=convertbits
        self.charset=charset 

        os.makedirs(self.workdir,exist_ok=True)
        self.atoms:list[atomTest]=[]
        
        for q in self.qlist:
            self.atoms.append(
                atomTest(
                    vspipe=self.vspipe,
                    vpypath=self.vpypath,
                    cmd=self.cmd,
                    q=q,
                    workdir=workdir,
                    output=output+f"_q{q}",
                    encoder=self.encoder,
                    metrics=self.metrics,
                    alt_vpypath=".converted.vpy" if self.convertbits>0 else self.vpypath 
                )
            )
        
    def run(self):
        if self.convertbits>0:
            with open(".converted.vpy","w",encoding=self.charset) as file:
                file.write(add_fmtc_bitdepth_for_vpy(self.vpypath,self.convertbits,self.charset))

        for atom in self.atoms:
            atom.run()
        if self.convertbits>0:
            os.remove(".converted.vpy")
            
    def collect_result(self) -> dict:
        results={}
        for atom in self.atoms:
            if atom.succuss>0:
                results[atom.q]=atom.collect_result()
        
        encode_settings={
            "source":self.vpypath,
            "encoder":self.encoder.encoder_path,
            "cmd":self.cmd,
            "name":self.name,
            "metrics":{m.name:m.provide for m in self.metrics}
        }
        res={
            "encode_settings":encode_settings,
            "results":results,
        }
        
        return res
    
    def check_result_file(self) -> int:
        """
        :return: -2:not match,-1:not found,0:everything is ok,1:partial ok(not all atomTest run succuss)
        :rtype: int
        """
        rfile=f"{os.path.join(self.workdir,self.output)}.json"
        if not os.path.exists(rfile):
            return -1
        
        res=loadjson(rfile)
        
        returncode=0
        try:
            if not res["encode_settings"]["source"]==self.vpypath:
                return -2
            if not res["encode_settings"]["cmd"]==self.cmd:
                return -2
            if not res["encode_settings"]["name"]==self.name:
                return -2
            for m in self.metrics:
                if m.name not in res["encode_settings"]["metrics"]:
                    return -2
                
                for p in m.provide:
                    if p not in res["encode_settings"]["metrics"][m.name]:
                        return -2
            
            eq=0        
            for q in self.qlist:
                if str(q) in res["results"]:
                    eq+=1
            returncode=0 if eq==len(self.qlist) else 1
            
        except:
            return -2
        
        return returncode
            
    
    def save_result(self):
        output=os.path.join(self.workdir,self.output)
        res=self.collect_result()
        
        with open(f"{output}.json",'w') as file:
            file.write(json.dumps(res))
