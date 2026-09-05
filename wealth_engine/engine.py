import math
MILESTONES=[2500000,5000000,10000000]

def years_to_target(current,target,cagr):
    if current>=target:return 0
    if current<=0 or cagr<=0:return None
    return math.log(target/current)/math.log(1+cagr)

def build_milestones(current_value,annual_return,annual_deployment=0):
    out=[]
    next_target=next((x for x in MILESTONES if x>current_value),MILESTONES[-1])
    for target in MILESTONES:
        out.append({"target":target,"gap":max(0,target-current_value),
                    "status":"CROSSED" if current_value>=target else ("NEXT" if target==next_target else "FUTURE"),
                    "years":years_to_target(current_value,target,annual_return),
                    "progress_pct":min(100,current_value/target*100)})
    return out

def deployment_impact(current,target,amount):
    return {"current_gap":max(0,target-current),"new_gap":max(0,target-current-amount),
            "gap_reduction":min(amount,max(0,target-current)),
            "progress_before":current/target*100,
            "progress_after":min(100,(current+amount)/target*100)}
