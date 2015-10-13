from proms_report import PromsReport
import pprint


#r01 = open('C:\\Users\car587\\ownCloud\\code\\rules_proms\\test\\proms_report\\test_proms_report_01.ttl').read()
r02 = open('C:\\Users\car587\\ownCloud\\code\\rules_proms\\test\\proms_report\\test_proms_report_02.ttl').read()
pr = PromsReport(r02)
pprint.pprint( pr.get_result())