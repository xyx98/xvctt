from .base import metric
import re
from ..utils import MEAN
import statistics
from enum import Enum
import json
import warnings

class vmaf_model(Enum):
    vmaf_v0_6_1=0,
    vmaf_v0_6_1_neg=1,
    vmaf_b_v0_6_3=2,
    vmaf_4k_v0_6_1=3,
    none=4


class vmaf(metric):
    def __init__(self,charset:str="utf-8",mean_mode:MEAN=MEAN.harmonic,model:vmaf_model=vmaf_model.vmaf_v0_6_1,extra_metrics:list[int]=[],use_vmaf_pool:bool=True):
        self.provide=[]
        self.name="vmaf"
        self.charset=charset
        self.mean_mode=mean_mode
        self.model=model
        self.extra_metrics=extra_metrics
        self.use_vmaf_pool=use_vmaf_pool
        self.use_vspipe=True
        
        if use_vmaf_pool:
            if self.mean_mode!=MEAN.average and self.mean_mode!=MEAN.harmonic:
                raise ValueError("when use_vmaf_pool,mean_mode only support average or harmonic")
        
        self.model_map=["vmaf","vmaf_neg","vmaf_b","vmaf_4k"]
        if not self.model==vmaf_model.none:
            self.provide.append(self.model_map[self.model.value[0]])
        
        self.extra_metrics_map=[
            ["psnr_y","psnr_cb","psnr_cr"],
            ["psnr_hvs"],
            ["float_ssim"],
            ["float_ms_ssim"],
            ["ciede2000"]
        ]
        for i in self.extra_metrics:
            self.provide+=self.extra_metrics_map[i]
            if i==0:
                self.provide.append("psnr_yuv") #for psnr,add weighted average 4:1:1 for yuv
        
    def genscript(self, orgscript:str,dstpath:str) -> str:
        if self.model==vmaf_model.none:
            model=None
        else:
            model=self.model.value[0]
        with open(orgscript,'r',encoding=self.charset) as file:
            script=file.read()
        
        rex=re.compile(r"(.+)\.set_output\(\)")
        
        match=rex.search(script)
        clip=match.group(1)
        
        feature=self.extra_metrics if self.extra_metrics else None
        
        script=rex.sub("",script)
        script+=f'\nimport xvs\n'
        script+=f'dst=core.lsmas.LWLibavSource(r"{dstpath}",cache=False)\n'
        script+=f'dst=core.resize.Spline36(dst,{clip}.width,{clip}.height,format={clip}.format)\n'
        script+=f'last=core.vmaf.VMAF({clip}, dst, log_path="{self.infopath(dstpath)}", log_format=1, model={model},feature={feature})\n'
        script+=f'last.set_output()'
        return script

    def run_without_vsipe(self, orgscript:str, dstpath:str):
        raise NotImplementedError("Not supported!")

    def infopath(self,dstpath:str,fin:bool=False) -> str:
        if fin:
            if self.model==vmaf_model.none:
                return f"{dstpath}_{self.name}_mnone_fin.json"
            else:
                return f"{dstpath}_{self.name}_m{self.model.value[0]}_fin.json"
        else:
            if self.model==vmaf_model.none:
                return f"{dstpath}_{self.name}_mnone.json"
            else:
                return f"{dstpath}_{self.name}_m{self.model.value[0]}.json"
    
    def getresult(self, infopath:str) -> dict[str,float|int]:
        with open(infopath,'r') as file:
            vmafdata=json.loads(file.read())
        
        if self.model==vmaf_model.none:
            model=None
        else:
            model=self.model_map[self.model.value[0]]
        
        if self.use_vmaf_pool:
            data=vmafdata["pooled_metrics"]
            meanmode="mean" if self.mean_mode==MEAN.average else "harmonic_mean"
            res={}
            for key in self.provide:
                if key=="psnr_yuv":
                    res[key]=(4*data["psnr_y"][meanmode]+data["psnr_cb"][meanmode]+data["psnr_cr"][meanmode])/6
                else:
                    res[key]=data[key][meanmode]
        else:
            data=vmafdata["frames"]
            reslists={}
            for key in self.provide:
                reslists[key]=[]
            res=dict.fromkeys(self.provide, -1)
            
            if self.mean_mode==MEAN.average:
                mean=statistics.fmean
            elif self.mean_mode==MEAN.harmonic:
                mean=statistics.harmonic_mean
            elif self.mean_mode==MEAN.geometric:
                mean=statistics.geometric_mean
            elif self.mean_mode==MEAN.quadratic:
                mean=lambda i: (sum(map(lambda x: x**2),i)/len(i))**0.5
            
            
            for frame in data:
                if model is not None:
                    score=frame["metrics"][model]
                    if score is None:
                        warnings.warn(f"{model} at frame {frame["frameNum"]} is None,will simply ingored")
                    else:
                        reslists[model].append(score)
                
                for i in self.extra_metrics:
                    for key in self.extra_metrics_map[i]:
                        score=frame["metrics"][key]
                        if score is None:
                            warnings.warn(f"{key} at frame {frame["frameNum"]} is None,will simply ingored")
                        else:
                            reslists[key].append(score)
                
                    if i==1:
                        if (frame["metrics"]["psnr_y"] or frame["metrics"]["psnr_cb"] or frame["metrics"]["psnr_cr"]) is not None:
                            reslists["psnr_yuv"].append((4*frame["metrics"]["psnr_y"]+frame["metrics"]["psnr_cb"]+frame["metrics"]["psnr_cr"])/6)
        
            for key in self.provide:
                res[key]=mean(reslists[key])
        
        return res
        
    