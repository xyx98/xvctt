from .singleTest import singleTest
from .encoders.base import encoder_base
from .metrics.base import metric
from .chart import ThemeType,chart
from .report import htmlreport
import os

class mainTest:
    def __init__(self,
            vpypath:str,
            title:str,
            metrics:metric|list[metric],
            theme=ThemeType.VINTAGE,
            vspipe:str="vspipe",
            workpath:str="workpath"
        ):
        self.vpypath=vpypath
        self.vspipe=vspipe
        self.title=title
        self.metrics=metrics if isinstance(metrics,list) else [metrics]
        self.theme=theme
        self.singles:list[singleTest]=[]
        self.workpath=workpath
        
    def add(self,encoder:encoder_base,cmd:str,qlist:list[int|float|str],output:str,workdir:str=""):
        realworkdir=f"{encoder.name}_{output}" if not workdir else workdir
        realworkdir=os.path.join(self.workpath,realworkdir)
        st=singleTest(
            vspipe=self.vspipe,
            vpypath=self.vpypath,
            cmd=cmd,
            qlist=qlist,
            workdir=realworkdir,
            output=output,
            encoder=encoder,
            metrics=self.metrics
        )
        self.singles.append(st)
            
    def run(self):
        for st in self.singles:
            st.run()
            st.save_result()
        
    def genreport(self,metrics_provider:str,metric_name:str,output:str|None=None,ref:int=0,embed_echarts:bool=False,calcbdrate:bool=True):
        if output is None:
            output=f"{metrics_provider}_{metric_name}.html"
        
        ref=min(max(0,ref),len(self.singles)-1)
        
        c=chart(self.title,metrics_provider,metric_name,embed_echarts,self.theme)
        
        datas=[]
        for st in self.singles:
            datas.append(st.collect_result())
        
        for d in datas:
            c.add_data(d)
            
        hr=htmlreport(c.render_to_string(),self.theme)
        for i in range(len(datas)):
            if i==ref:
                hr.add_ref(datas[i])
            else:
                hr.add_data(datas[i])
        
        hr.gen_report(metrics_provider,metric_name,calcbdrate)
        hr.save(output)
    
    def genreport_all(self,report_dir:str="reports",ref:int=0,embed_echarts:bool=False,calcbdrate:bool=True):
        if report_dir!="" or report_dir!=".":
            os.makedirs(report_dir,exist_ok=True)
        
        for mp in self.metrics:
            metrics_provider=mp.name
            for m in mp.provide:
                metric_name=m
                if report_dir=="" or report_dir==".":
                    output=f"{metrics_provider}_{metric_name}.html"
                else:
                    output=os.path.join(report_dir,f"{metrics_provider}_{metric_name}.html")
                
                self.genreport(metrics_provider,metric_name,output,ref,embed_echarts,calcbdrate)
                
