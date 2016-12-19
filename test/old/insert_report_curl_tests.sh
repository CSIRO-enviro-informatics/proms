# post a correct ANUGA Report
# we expect a 201 Inserted response
curl -i --request POST -H "Content-Type: text/turtle" -d@example_report_ANUGA.ttl http://proms-dev.vhirl.net/id/report/

# post a Report missing a nativeId
# we expect a 400 response with the error message "Insert failed for the following reasons: The Report class does not contain a proms:nativeId"
curl -i --request POST -H "Content-Type: text/turtle" -d@example_report_ANUGA_broken.ttl http://proms-dev.vhirl.net/id/report/
