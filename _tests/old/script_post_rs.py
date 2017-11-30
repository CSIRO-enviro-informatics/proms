import sys
import requests
import imp
settings = imp.load_source('', 'c:/work/proms/__init__.py')

"""
# python script_post_rs.py {RS_TURTLE_FILE}
"""
with open(sys.argv[1], 'rb') as payload:
    if settings.PROMS_INSTANCE_NAMESPACE_URI.endswith('/'):
        rs_register_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + 'id/reportingsystem/'
    else:
        rs_register_uri = settings.PROMS_INSTANCE_NAMESPACE_URI + '/id/reportingsystem/'
    r = requests.post(rs_register_uri,
                      data=payload,
                      headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.content