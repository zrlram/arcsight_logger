#!/usr/bin/python
#
# Copyright (c) 2012 by PixlCloud LLC
#
#

import suds
from suds.xsd.doctor import Import, ImportDoctor

from datetime import datetime, timedelta
import time, sys

user = "raffy"
password = "password"
server = "https://my.machine.com:9090/soap/services/"
query = "BitTorrent | fields - _EventTime - _PeerName - _raw | cef name sourceAddress destinationAddress destinationPort"
start = int(time.mktime((datetime.now() - timedelta(minutes=800)).timetuple())) * 1000
#end = int(time.mktime((datetime.now() - timedelta(minutes=480)).timetuple())) * 1000
end = int(time.mktime((datetime.now()).timetuple())) * 1000

# SOAP URLs
xsd = "http://www.arcsight.com/logger/xsd"
ns = 'http://domain.login.webservices.logger.arcsight.com/xsd'
ns2 = 'http://domain.search.webservices.logger.arcsight.com/xsd'
login = "%sLoginService/LoginService.wsdl" % server
search = "%sSearchService/SearchService.wsdl" % server

# Setup Logging
import logging
logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
#logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)

imp = Import(xsd)
imp.filter.add(ns)
imp.filter.add(ns2)
doctor = ImportDoctor(imp)

# login
login_client = suds.client.Client(url=login, doctor=doctor, location=login)

token = login_client.service.login(user, password)
if not token:
    sys.stderr.write("Failed to log in")
    exit(1)

print "Login successful"

# search
client = suds.client.Client(url=search, doctor=doctor, location=search)
search = client.service.startSearch(query, start, end, token)
print client.service.getHeader(token)
while client.service.hasMoreTuples(token):
    res = client.service.getNextTuples(20, 8000, token)     # count, timeout, token
    for r in res:
        print r[0]

client.service.endSearch(token)
login_client.service.logout(token)
