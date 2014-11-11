import json
import os
from rulesets import proms

from rdflib import Graph, Literal, URIRef
import requests

'''
#test incoming doc conformance
p = proms.Proms(open('/var/lib/proms/test/ddg_report.ttl').read())
print json.dumps(p.get_result()['rule_results'][0]['passed'])
if len(p.get_result()['rule_results'][0]['fail_reasons']) > 0:
    print json.dumps(p.get_result()['rule_results'][0]['fail_reasons'])

print json.dumps(p.get_result())
'''

#
# test insert into Stardog
#
#get the data into a graph
g = Graph()
g.parse(open('/var/lib/proms/test/ddg_report.ttl'), format="n3")
#put data into a SPARQL 1.1 INSERT DATA query
insert_query = 'INSERT DATA {' + g.serialize(format='n3') + '}'

#insert into Stardog using the HTTP API
url = 'http://localhost:5820/proms/update'
h = {'content-type': 'application/sparql-update'}
r = requests.post(url, data=insert_query, headers=h, auth=('proms', 'proms'))

if r.status_code == 200:
    print 'INSERTED'
else:
    print r.text