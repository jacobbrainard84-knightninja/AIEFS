import urllib.request, urllib.parse, re, json, time
import os
LOG=os.path.join(os.path.dirname(os.path.abspath(__file__)),"arxiv_search_log.json")  # next to this script
qs=[
 'abs:Kuramoto AND abs:"adaptive" AND abs:delay AND abs:plasticity',
 'abs:"phase oscillators" AND abs:"conserved" AND abs:coupling AND abs:adaptive',
 'abs:Hebbian AND abs:Kuramoto AND abs:"phase-locking"',
 'abs:"adaptive coupling" AND abs:Kuramoto AND abs:"phase-locked" AND abs:"sufficient"',
 'abs:"multiplicative normalization" AND abs:Hebbian',
 'abs:"homeostatic" AND abs:"Kuramoto"',
 'abs:"network topology" AND abs:"finite time" AND abs:"adaptive" AND abs:synchronization',
 'abs:"coevolution" AND abs:"phase oscillators" AND abs:"pruning"',
 'abs:"Kuramoto" AND abs:"adaptive" AND abs:"capacity"',
 'abs:"discrete-time" AND abs:"adaptive" AND abs:"Kuramoto" AND abs:"Hebbian"',
 'abs:"linear recurrence" AND abs:"bounded" AND abs:"eventually" AND abs:"sign"',
 'abs:"STDP" AND abs:"hard bounds" AND abs:"bimodal"',
]
log=[]
for q in qs:
    url='https://export.arxiv.org/api/query?'+urllib.parse.urlencode({'search_query':q,'max_results':12,'sortBy':'relevance'})
    try:
        x=urllib.request.urlopen(url,timeout=60).read().decode()
        tot=re.search(r'<opensearch:totalResults[^>]*>(\d+)<',x); tot=tot.group(1) if tot else '?'
        ents=re.findall(r'<entry>.*?<id>(.*?)</id>.*?<title>(.*?)</title>',x,re.S)
        log.append(dict(query=q,total=tot,top=[(i.strip(),' '.join(t.split())) for i,t in ents]))
    except Exception as e: log.append(dict(query=q,error=str(e)))
    print(json.dumps(log[-1])[:2500],flush=True); time.sleep(3.5)
old=json.load(open(LOG))
json.dump({'date':'2026-10-28','endpoint':'https://export.arxiv.org/api/query','queries':old+log},open(LOG,'w'),indent=1)
