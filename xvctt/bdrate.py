import bjontegaard as bd

def is_increasing(bitrate:list[int|float],score:list[int|float]) -> bool:
    zipped = list(zip(bitrate, score))
    sorted_zipped = sorted(zipped, key=lambda x: x[0])
    for i in range(1,len(sorted_zipped)):
        if not sorted_zipped[i][1] > sorted_zipped[i-1][1]:
            return False
    
    return True
        

def bdrate(ref_data:dict,test_data:dict,metric_provider:str,metric_name:str,method='akima') -> float|None:
    ref_rate=[]
    ref_metric=[]
    for k,v in ref_data["results"].items():
        ref_rate.append(v["bitrate"])
        ref_metric.append(v["metrics"][metric_provider][metric_name])
    
    if not is_increasing(ref_rate,ref_metric):
        return
    
    
    test_rate=[]
    test_metric=[]
    for k,v in test_data["results"].items():
        test_rate.append(v["bitrate"])
        test_metric.append(v["metrics"][metric_provider][metric_name])
    
    if not is_increasing(test_rate,test_metric):
        return
    
    try:
        res=bd.bd_rate(ref_rate, ref_metric, test_rate, test_metric, method=method,min_overlap=0,require_matching_points=False)
    except:
        return
    
    if res==res: 
        return res
    else: # check whether res is nan.
        return