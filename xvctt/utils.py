import os
import statistics
from enum import Enum
import vapoursynth as vs
import functools
import json
import re

class MEAN(Enum):
    harmonic=0,
    average=1,
    quadratic=2,
    geometric=3

def applybackspace(s:str) -> str:
    tmp=[]
    for i in s:
        if i!="\b":
            tmp.append(i)
        elif len(tmp)>0:
            tmp.pop()
    return "".join(tmp)


def cls() -> None:
    if os.name=="nt":
        os.system("cls")
    else:
        os.system("clear")
        
def calcbitrate(file:str,length:int|float) -> float:
    """
    file: file path
    length: should be ms
    return is kbps
    """
    fsize=os.path.getsize(file)
    return fsize/length * 8

def calcfps(frames:int,time:int|float) -> float:
    """
    frames: total frames
    time: encode time,should be s
    """
    return frames/time

def get_video_info_by_vs(vpath:str) -> dict[str,float|int]:
    core=vs.core
    sourcefilters=[]
    if hasattr(core,'bs'):
        sourcefilters.append(functools.partial(core.bs.VideoSource,cachemode=0))
    if hasattr(core,'lsmas'):
        sourcefilters.append(functools.partial(core.lsmas.LWLibavSource,cache=False))
    if hasattr(core,'ffms2'):
        sourcefilters.append(functools.partial(core.ffms2.Source,cache=False))
        
    for sf in sourcefilters:
        try:
            clip:vs.VideoNode=sf(vpath)
            frames=clip.frames
            fpsnum=clip.fps_num
            fpsden=clip.fps_den
            width=clip.width
            height=clip.height
            duration=frames/fpsnum*fpsden #s
        except:
            continue
        else:
            return {
                "frames":frames,
                "fpsnum":fpsnum,
                "fpsden":fpsden,
                "width":width,
                "height":height,
                "duration":duration
            }
    
    return {
        "frames":-1,
        "fpsnum":-1,
        "fpsden":-1,
        "width":-1,
        "height":-1,
        "duration":-1
    }
    
def loadjson(p:str) -> dict|list:
    with open(p,'r') as file:
        data=json.loads(file.read())
    return data

def add_fmtc_bitdepth_for_vpy(vpypath:str,bitdepth:int,charset:str="utf-8") -> str:
    with open(vpypath,'r',encoding=charset) as file:
        script=file.read()

    rex=re.compile(r"(.+)\.set_output\(\)")
    match=rex.search(script)
    clip=match.group(1)
    script=rex.sub("",script)
    script+=f"{clip}=core.fmtc.bitdepth({clip},bits={bitdepth},dmode=1)\n"
    script+=f"{clip}.set_output()"
    return script