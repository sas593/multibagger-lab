def filter_material(news):
    return [n for n in news if n.materiality in {"Material","Critical"}]

def classify_threat(news):
    out=[]
    for n in filter_material(news):
        level="Material Risk" if n.category=="Competitive" else "Thesis Threat" if n.category=="Governance" else "Watch" if n.category in {"Financial","Market"} else "Normal"
        out.append({"Ticker":n.ticker,"Date":n.published_at,"Headline":n.headline,"Category":n.category,"Threat":level,"Thesis Impact":n.thesis_impact})
    return out
