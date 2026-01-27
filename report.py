from bs4 import BeautifulSoup
import warnings

from .bdrate import bdrate
from .chart import ThemeType,theme_color

class htmlreport:
    def __init__(self,html:str,theme=ThemeType.VINTAGE):
        self.html=html
        self.soup=None
        self.ref=None #for bdrate
        self.datas=[]
        self.css="""<style>
                body{
                    background-color:{{{bgcolor}}};
                    color: {{{titlecolor}}};
                }
                h3{
                    font-size:30px;
                }
                table{
                    width:100%;
                    font-size:24px;
                }
                td{
                    padding-right: 2em;
                    color:{{{subcolor}}}
                }
                th{
                    text-align: left;
                    padding-right: 2em;
                }
                .ref{
                    font-weight: bold;
                }
                .col0{
                    width:10%
                }
                .col1{
                    width:10%;
                }
                .col2{
                    width:10%;
                }
                .col3{
                    width:15%;
                }
                .col4{
                    width:10%
                }
                .col5{
                    width:45%
                }
                </style>"""
        self.css=self.css.replace("{{{bgcolor}}}",theme_color[theme]['bg'])
        self.css=self.css.replace("{{{titlecolor}}}",theme_color[theme]['title'])
        self.css=self.css.replace("{{{subcolor}}}",theme_color[theme]['sub'])

    def add_data(self,data:dict):
        if data not in self.datas:
            self.datas.append(data)

    def add_ref(self,data:dict,addtodata:bool=True):
        if self.ref is None:
            self.ref=data
        else:
            raise ValueError("htmlreport:you can set ref only once.")
        
        if addtodata:
            self.add_data(data)

    def gen_report(self,metrics_provider:str,metric_name:str,calcbdrate:bool=True):
        self.soup=BeautifulSoup(self.html,"html.parser")
        self.soup.head.append(BeautifulSoup(self.css,"html.parser"))
        script = self.soup.body.find('script')
        script.string+="""
        w=window.innerWidth*0.8;
        h=w/16*9;
        chart_metrics_provider_metric_name.resize({width:w+'px',height:h+'px'});
        var divs = document.getElementsByTagName("div");
        divs[0].style.width =w+'px';
        divs[0].style.height=h+'px';
        """.replace("metrics_provider_metric_name",f"{metrics_provider}_{metric_name}")
        
        resize_script = self.soup.new_tag("script")
        resize_script.string="""
        function resize(){
        w=window.innerWidth*0.8;
        h=w/16*9
        chart_metrics_provider_metric_name.resize({width:w+'px',height:h+'px'});
        var divs = document.getElementsByTagName("div");
        divs[0].style.width =w+'px';
        divs[0].style.height=h+'px';
        }
        window.addEventListener("resize",resize);
        """.replace("metrics_provider_metric_name",f"{metrics_provider}_{metric_name}".replace('-','_'))
        self.soup.body.append(resize_script)
        
        
        if calcbdrate and self.ref is None:
            warnings.warn("For calculate bd-rate,ref must set!\nbd-rate calculation disabled.")
        
        
        for data in self.datas:
            isref=data==self.ref
            head=["quality","bitrate","speed",metric_name]
            #extitle=["bd-rate"] if calcbdrate else []

            
            if isref:
                table=f"</br><h3 class=ref>{data["encode_settings"]["name"]}</h3>"
                table+="<table class=ref><tbody><tr>"
            else:
                table=f"</br><h3>{data["encode_settings"]["name"]}</h3>"
                table+="<table><tbody><tr>"
            
            #<th>"+"</th><th>".join(head+extitle+[""])+"</th>{lines}</tbody></table>"
            for i in range(len(head)):
                table+=f"<th class=col{i}>{head[i]}</th>"
            if calcbdrate:
                table+="<th class=col4>bd-rate</th>"
            table+=f"<th class=col5></th>"
            table+="{lines}</tbody></table>"
            
            lines=""
            lenq=len(data["results"])
            isfirst=True
            for q,r in data["results"].items():
                lines+=f"<tr><td>{q}</td><td>{r["bitrate"]}</td><td>{r["fps"]} fps</td>"
                lines+=f"<td>{r["metrics"][metrics_provider][metric_name]}</td>"
                
                if isfirst:
                    if calcbdrate:
                        bdrate_res=bdrate(self.ref,data,metrics_provider,metric_name)
                        bdrate_res=f"{bdrate_res:.02f}%" if bdrate_res else "N/A"
                        lines+=f"<td rowspan={lenq}>{bdrate_res}</td>"
                    
                    lines+=f"<td rowspan={lenq}>{data["encode_settings"]["encoder"].strip()} {data["encode_settings"]["cmd"].strip()}</td>"
                    isfirst=False
                lines+="</tr>"
            table=table.format(lines=lines)
            self.soup.body.append(BeautifulSoup(table,"html.parser"))
        
    def save(self,output:str):
        with open(output,"w",encoding="utf-8") as file:
            file.write(self.soup.prettify())
        