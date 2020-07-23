#!/usr/bin/python3
import re
#from ptsite import *

"""
tSite = None
for site in NexusPage.site_list:
    if 'FRDS' == site['name']: 
        tSite = site
        break
print("find site:{}".format(tSite['name']))
            
tPage = NexusPage(tSite)
if not tPage.request_detail_page('11252'):
    print("failed to request detail")
"""

temp = {
        'name':'name',
        'agent':'agent'}


print( temp.get('name'))
print( temp.get('host'))

up_val = ("122",1,3)
temp = "{}".format(up_val)
print(type(temp))
print(temp)
print(up_val[0])

sql='update rss set download=%s where rssname=%s and hash=%s'
val=(1,'mteam',"xxxx")
print("error sql:{}|{}".format(sql,val))
print(len(val))
i = 0
for i in range(len(val)):
    tIndex = sql.find('%s')
    if tIndex == -1:
        break
    sql = sql.replace('%s',str(val[i]),1)
    print(sql)
if i != len(val)-1: print("error")
