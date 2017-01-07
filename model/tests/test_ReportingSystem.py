import database
import tests.example_data_tests
from model.reportingsystem import ReportingSystemRenderer

# start afresh
tests.example_data_tests.purge_db()
# load an RS
tests.example_data_tests.load_rs()
# get the RS graph
rs_uri = 'http://pid.geoscience.gov.au/system/system-01'
g = database.get_class_object_graph(rs_uri)

rsr = ReportingSystemRenderer(g, rs_uri)
print rsr._get_details()
