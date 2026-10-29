import urllib.request, urllib.parse, re, json, time, sys
import os
LOG=os.path.join(os.path.dirname(os.path.abspath(__file__)),"arxiv_search_log.json")  # next to this script
qs=[
 'all:"adaptive Kuramoto" AND all:"finite time"',
 'abs:adaptive AND abs:Kuramoto AND abs:topology AND abs:frozen',
 'abs:"Hebbian" AND abs:"Kuramoto" AND abs:"normalization"',
 'abs:"Hebbian" AND abs:"oscillators" AND abs:"budget"',
 'abs:"adaptive couplings" AND abs:"Kuramoto" AND abs:"synchronization"',
 'abs:"adaptive network" AND abs:"eventually constant"',
 'abs:"Hebbian" AND abs:"hard bounds" AND abs:"finite time"',
 'abs:"synaptic normalization" AND abs:"Hebbian" AND abs:"convergence"',
 'abs:"Kuramoto" AND abs:"time delay" AND abs:"adaptive coupling"',
 'abs:"ultimate positivity" AND abs:"linear recurrence"',
 'abs:"eventual sign" AND abs:"recurrence" AND abs:"perturbation"',
 'abs:"threshold" AND abs:"adaptive network" AND abs:"topology" AND abs:"converge" AND abs:"finite"',
]
log=[]
for q in qs:
    url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'max_results':15,'sortBy':'relevance'})
    try:
        x=urllib.request.urlopen(url,timeout=60).read().decode()
        tot=re.search(r'<opensearch:totalResults[^>]*>(\d+)<',x); tot=tot.group(1) if tot else '?'
        ents=re.findall(r'<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>',x,re.S)
        log.append(dict(query=q,total=tot,top=[(i.strip(),' '.join(t.split())) for i,t in ents]))
    except Exception as e: log.append(dict(query=q,error=str(e)))
    print(json.dumps(log[-1])[:3000],flush=True); time.sleep(3.5)
json.dump(log,open(LOG,'w'),indent=1)
