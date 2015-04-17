import requests

# post a correct ANUGA Report
# we expect a 201 Inserted response
with open('example_report_ANUGA.ttl','rb') as payload:
	r = requests.post('http://proms-dev.vhirl.net/id/report/', 
			  data=payload,
			  headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.text


# post a Report missing a nativeId
# we expect a 400 response with the error message "Insert failed for the following reasons: The Report class does not contain a proms:nativeId"
with open('example_report_ANUGA_broken.ttl','rb') as payload:
	r = requests.post('http://proms-dev.vhirl.net/id/report/', 
			  data=payload,
			  headers={'Content-Type': 'text/turtle'})

print r.status_code
print r.text

