import requests
import _config as conf

# post a Report missing a nativeId
# we expect a 400 response with the error message "Insert failed for the following reasons: The Report class does not contain a proms:nativeId"
with open('../rulesets/rulesets/reports/_tests/external_report_pass.ttl', 'rb') as payload:
    r = requests.post(conf.REPORT_BASE_URI + '/',
                      data=payload,
                      headers={'Content-Type': 'text/turtle'})

print(r.status_code)
print(r.text)

