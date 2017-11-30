import requests

# post a Report missing a nativeId
# we expect a 400 response with the error message "Insert failed for the following reasons: The Report class does not contain a proms:nativeId"
with open('../rulesets/rulesets/reportingsystems/_tests/rs_pass.ttl', 'rb') as payload:
    r = requests.post('http://localhost:9000/id/reportingsystem/',
                      data=payload,
                      headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.text

