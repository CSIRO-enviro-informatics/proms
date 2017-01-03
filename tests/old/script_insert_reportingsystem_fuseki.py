import sys
import requests

with open(sys.argv[1], 'rb') as payload:
    d = payload.read()
    r = requests.post('http://localhost:3030/tdb/upload',
                      data=d,
                      headers={'Content-Type': 'text/turtle'}
    )


print r.status_code
print r.content