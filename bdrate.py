import bjontegaard as bd

def bdrate(ref_data:dict,test_data:dict,metric_provider:str,metric_name:str,method='akima') -> float:
    ref_rate=[]
    ref_metric=[]
    for k,v in ref_data["results"].items():
        ref_rate.append(v["bitrate"])
        ref_metric.append(v["metrics"][metric_provider][metric_name])
    
    test_rate=[]
    test_metric=[]
    for k,v in test_data["results"].items():
        test_rate.append(v["bitrate"])
        test_metric.append(v["metrics"][metric_provider][metric_name])
    
    return bd.bd_rate(ref_rate, ref_metric, test_rate, test_metric, method=method,min_overlap=0,require_matching_points=False)