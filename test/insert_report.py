import requests

# post a Report missing a nativeId
# we expect a 400 response with the error message "Insert failed for the following reasons: The Report class does not contain a proms:nativeId"
with open('../proms_rulesets/rulesets/reports/test/external_report_pass.ttl', 'rb') as payload:
    r = requests.post('http://localhost:9000/id/report/',
                      data=payload,
                      headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.text

