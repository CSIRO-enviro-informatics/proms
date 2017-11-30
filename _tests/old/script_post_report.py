import sys
import requests
from datetime import datetime
import imp
settings = imp.load_source('', 'c:/work/proms/__init__.py')

"""
# python script_post_rs.py {REPORT_TURTLE_FILE} {RS_URI}
"""
with open(sys.argv[1], 'rb') as payload:
    # replace the RS URI with a given one
    d = payload.read()
    d = d.replace('{{REPORTING_SYSTEM_URI}}', sys.argv[2])
    d = d.replace('{{GENERATED_AT_TIME}}', datetime.now().isoformat())

    if settings.PROMS_INSTANCE_NAMESPACE_URI.endswith('/'):
        rs_register_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/report/'
    else:
        rs_register_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + '/id/report/'
    r = requests.post(rs_register_uri,
                      data=d,
                      headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.content