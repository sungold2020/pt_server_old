#!/usr/bin/python3
import re
from ptsite import *

tSite = None
for site in NexusPage.site_list:
    if 'FRDS' == site['name']: 
        tSite = site
        break
print("find site:{}".format(tSite['name']))
            
tPage = NexusPage(tSite)
if not tPage.request_detail_page('11252'):
    print("failed to request detail")

