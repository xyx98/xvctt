from pyecharts.charts import Line
import pyecharts.options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons import utils as pyecharts_utils
from pyecharts.render import engine
from typing import Any

def render_chart_to_string(self, template_name: str, chart: Any, **kwargs):
    """
    hack pyecharts for render to string
    """
    tpl = self.env.get_template(template_name)
    html = pyecharts_utils.replace_placeholder(
        tpl.render(chart=self.generate_js_link(chart), **kwargs)
    )
    return html

engine.RenderEngine.render_chart_to_string=render_chart_to_string

theme_color={
    "light"         :{'bg':'rgba(0,0,0,0)','title':"#464646",'sub':'#6E7079'},
    "dark"          :{'bg':'rgba(51,51,51,1)','title':"#eeeeee",'sub':'#aaa'},
    "white"         :{'bg':'rgba(0,0,0,0)','title':"#464646",'sub':'#6E7079'},
    "chalk"         :{'bg':'rgba(41,52,65,1)','title':"#ffffff",'sub':'#dddddd'},
    "essos"         :{'bg':'rgba(242,234,191,0.15)','title':"#893448",'sub':'#d95850'},
    "infographic"   :{'bg':'rgba(0,0,0,0)','title':"#27727b",'sub':'#6E7079'},
    "macarons"      :{'bg':'rgba(0,0,0,0)','title':"#008acd",'sub':'#aaa'},
    "purple-passion":{'bg':'rgba(91,92,110,1)','title':"#ffffff",'sub':'#cccccc'},
    "roma"          :{'bg':'rgba(0,0,0,0)','title':"#333333",'sub':'#aaa'},
    "romantic"      :{'bg':'#f0e8cd','title':"#330022",'sub':'#3d2f1b'},
    "shine"         :{'bg':'rgba(0,0,0,0)','title':"#333333",'sub':'#aaa'},
    "vintage"       :{'bg':'rgba(254,248,239,1)','title':"#333333",'sub':'#aaa'},
    "walden"        :{'bg':'rgba(252,252,252,0)','title':"#666666",'sub':'#999999'},
    "westeros"      :{'bg':'rgba(0,0,0,0)','title':"#516b91",'sub':'#93b7e3'},
    "wonderland"    :{'bg':'rgba(255,255,255,0)','title':'#666666','sub':'#999999'},
    "halloween"     :{'bg':'rgba(64,64,64,0.5)','title':"#ffaf51",'sub':'#eeeeee'},
}



class chart:
    def __init__(self,title:str,metrics_provider:str,metrics_name:str,embed_echarts:bool=False,theme=ThemeType.VINTAGE):
        self.title=title
        self.metrics_provider=metrics_provider
        self.metrics_name=metrics_name
        self.embed_echarts=embed_echarts
        lenm=len(self.metrics_name)
        self.chart=(
            Line(
                init_opts=opts.InitOpts(
                    page_title=self.title,
                    theme=theme,
                    width="1280px",
                    height="720px",
                    chart_id=f"{metrics_provider}_{metrics_name}".replace('-','_'),
                ),
                render_opts=opts.RenderOpts(embed_echarts)
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title=self.title),
                xaxis_opts=opts.AxisOpts(
                    type_="value",
                    is_scale=True,
                    split_number=10,
                    name="bitrate/kbps",
                    axislabel_opts=opts.TextStyleOpts(font_size=16)
                    ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    is_scale=True,
                    name=self.metrics_name,
                    axislabel_opts=opts.TextStyleOpts(font_size=16)
                    ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    orient="horizontal",
                    pos_left="right",
                    feature=opts.ToolBoxFeatureOpts(
                        save_as_image=opts.ToolBoxFeatureSaveAsImageOpts(title="save as image",is_show=True),
                        restore=opts.ToolBoxFeatureRestoreOpts(is_show=True),
                        data_zoom=opts.ToolBoxFeatureDataZoomOpts(is_show=False),
                        data_view=opts.ToolBoxFeatureDataViewOpts(is_show=False,is_read_only=True,title="data"),
                        magic_type=opts.ToolBoxFeatureMagicTypeOpts(is_show=False),
                        brush=opts.ToolBoxFeatureBrushOpts(type_=[])
                        )
                    ),
                legend_opts=opts.LegendOpts(pos_top="bottom"),
                tooltip_opts=opts.TooltipOpts(
                    is_show=True,
                    textstyle_opts=opts.TextStyleOpts(font_size=16),
                    formatter=pyecharts_utils.JsCode("function(x) {lenm="+str(lenm)+";n1=lenm>7?lenm-7:0;n2=lenm>7?0:7-lenm;return x.seriesName + '<br/>bitrate&nbsp;&nbsp;&nbsp;&nbsp;'+'&nbsp;'.repeat(n1)+ x.data[0] + '&nbsp;kbps<br/>"+self.metrics_name+"&nbsp;&nbsp;&nbsp;&nbsp;'+'&nbsp'.repeat(n2) + x.data[1];}"),
                    background_color=theme_color[theme]['bg'],
                    axis_pointer_type="cross",
                ),
            )
        )
    
    def add_data(self,data):
        x_data=[]
        y_data=[]
        for k,v in data["results"].items():
            x_data.append(v["bitrate"])
            y_data.append(v["metrics"][self.metrics_provider][self.metrics_name])
        
        self.chart.add_xaxis(x_data)
        self.chart.add_yaxis(
            series_name=data["encode_settings"]["name"],
            y_axis=y_data,
            is_connect_nones=True,
            is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1,curve=10),
            symbol_size=12,
        )
    
    def render(self,output:str):
        self.chart.render(output)
        
    def render_to_string(self) -> str:
        self.chart._prepare_render()
        html=engine.RenderEngine().render_chart_to_string("simple_chart.html",chart=self.chart)
        return html