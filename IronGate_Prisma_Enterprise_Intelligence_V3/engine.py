import re, json
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
ROOT=Path(__file__).parent/'data'
DOCS=json.loads((ROOT/'policies.json').read_text())
DOCS += [dict(id=i,title=t,text=s) for i,t,s in [('O01','Capacity escalation','Validate bed occupancy, emergency department wait times and staffed capacity with operations leaders before escalation.'),('O02','Discharge coordination','Review delayed discharges and documented barriers with authorized care coordination staff.'),('O03','Staffing coverage','Validate staffing gaps and unfilled shifts with staffing leads; evaluate approved coverage options.'),('C01','Cost variation review','Compare equivalent periods and validate case mix, volume and unit cost before attributing cost increases.'),('C02','Utilization review','Investigate service utilization and volume changes with finance and clinical leaders; preserve quality safeguards.'),('C03','Contract review','Validate unit cost changes against approved contracts and accounting definitions before estimating savings.')]]
PREFIX={'Recover revenue':'P','Improve operations':'O','Reduce costs':'C'}
def search(module,q):
    docs=[d for d in DOCS if d['id'].startswith(PREFIX[module])]
    v=TfidfVectorizer(stop_words='english',ngram_range=(1,2)); m=v.fit_transform([d['title']+' '+d['text'] for d in docs]); scores=cosine_similarity(v.transform([q]),m)[0]
    return [dict(d,score=float(s)) for s,d in sorted(zip(scores,docs),key=lambda x:x[0],reverse=True)[:3] if s>0]
def analyze(module,q):
    q=q.lower()
    if module=='Recover revenue':
        d=pd.read_csv(ROOT/'denials.csv'); filters=[]
        for reason in d.reason.unique():
            if reason.lower() in q: filters.append(reason)
        if filters: d=d[d.reason.isin(filters)]
        age=re.search(r'(?:over|older than|at least|aged|>=)\s*(\d+)',q)
        if age or 'aging' in q: d=d[d.age_days>= (int(age.group(1)) if age else 30)]
        for f in d.facility.unique():
            if f.lower() in q: d=d[d.facility==f]; break
        if 'payer' in q: raise ValueError('Payer identifiers are not available in this synthetic dataset.')
        if not re.search(r'denial|denied|revenue|claim|authorization|eligibility|coding|filing|aging|appeal',q): raise ValueError('Ask about denied revenue, claim reasons, facility or aging.')
        group='facility' if 'facility' in q or 'hospital' in q else 'reason'; g=d.groupby(group,as_index=False).agg(claims=('claim_id','count'),denied_amount=('denied_amount','sum')).sort_values('denied_amount',ascending=False)
        if g.empty: raise ValueError('No matching synthetic records.')
        r=g.iloc[0]; return g,f'{r[group]} leads the selected grouping with ${r.denied_amount:,.0f} in denied amounts. Total in scope: ${d.denied_amount.sum():,.0f}. Denied amounts are not guaranteed recoveries.',str(r[group])+' denial prioritization appeal deadlines'
    if module=='Improve operations':
        d=pd.read_csv(ROOT/'operations.csv');d['occupancy']=d.occupied_beds/d.staffed_beds
        field=next((f for words,f in [('discharge','delayed_discharges'),('staff|shift','staffing_gap'),('wait|emergency|ed ','ed_wait_minutes'),('capacity|occupancy|bed','occupancy')] if re.search(words,q)),None)
        if not field: raise ValueError('Ask about capacity, ED wait, staffing or discharge delays.')
        d=d.sort_values(field,ascending=False);r=d.iloc[0]; value=f'{r[field]:.1%}' if field=='occupancy' else str(r[field]);return d,f'{r.facility} ranks highest on {field.replace("_"," ")}: {value}. This snapshot does not establish causes.',field.replace('_',' ')
    d=pd.read_csv(ROOT/'costs.csv');d['change']=d.current_volume*d.current_unit_cost-d.prior_volume*d.prior_unit_cost;d['volume_effect']=(d.current_volume-d.prior_volume)*d.prior_unit_cost;d['unit_cost_effect']=d.current_volume*(d.current_unit_cost-d.prior_unit_cost)
    field='unit_cost_effect' if 'unit cost' in q or 'unit-cost' in q else 'volume_effect' if 'volume' in q or 'utilization' in q else 'change'
    if not re.search(r'cost|spend|expenditure|volume|utilization',q): raise ValueError('Ask about cost changes, volume or unit cost.')
    d=d.sort_values(field,ascending=False);r=d.iloc[0];return d,f'{r.service} has the largest {field.replace("_"," ")}: ${r[field]:,.0f}. Total cost change: ${d.change.sum():,.0f}. Variation is not proof of avoidable expense.',field.replace('_',' ')+' cost review'
