def thesis_monitor(score, news):
    threats=[n.headline for n in news if n.thesis_impact.lower().startswith("negative")]
    if not score.hard_gates.get("Governance",True): threats.append("Governance risk gate failed")
    if not score.hard_gates.get("Cash Flow",True): threats.append("Operating cash flow gate failed")
    return {"status":"THESIS UNDER REVIEW" if threats else ("THESIS INTACT" if score.total>=70 else "THESIS WEAKENING"),
            "threats":threats}
