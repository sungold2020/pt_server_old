#!/usr/bin/python3
from bs4 import BeautifulSoup
import time
import requests
import os
import json
import lxml
import re

from info import *

site_url = 'https://movie.douban.com/people/69057957/collect?start=0&sort=time&rating=all&filter=all&mode=grid'
site_cookie = 'll="118282"; bid=p0dhpEfEV-4; __utmc=30149280; __utmc=223695111; __yadk_uid=zONgmuQAhUz48FScpbbLwlyp9sWgxc8m; _vwo_uuid_v2=DB07B9A9429A767628851B0838F87F143|70668c6e9c14c93aa7249d070dc6cf07; push_doumail_num=0; __utmv=30149280.21843; __gads=ID=af7d0ac47d706c3b:T=1592790195:S=ALNI_MZPqMSCLzv4tlBWoABDl8fGGwGUBQ; douban-profile-remind=1; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1594774016%2C%22https%3A%2F%2Fwww.douban.com%2Fpeople%2F218434462%2F%22%5D; _pk_ses.100001.4cf6=*; dbcl2="69057957:2mK8haBl60U"; ck=ysVQ; ap_v=0,6.0; _pk_id.100001.4cf6=e6366f0e1d0169b1.1586329544.7.1594774078.1594700240.; __utma=30149280.531319256.1586329544.1594700148.1594774078.8; __utmb=30149280.0.10.1594774078; __utmz=30149280.1594774078.8.3.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; __utma=223695111.1308861375.1586329544.1594700148.1594774078.7; __utmb=223695111.0.10.1594774078; __utmz=223695111.1594774078.7.2.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; push_noty_num=1'
user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36"
my_headers = {}
my_headers['User-Agent'] = user_agent

def find_end_number(mString):
    #  1-15 / 374
    mString = mString.strip('\n')
    mString = mString.strip()
    #print('-----------------')
    print(mString)
    #print('-----------------')
    
    tIndex = mString.find('-')
    if tIndex == -1: 
        ExecLog("can't find -:"+mString)
        return -1
    tStartNumber = mString[:tIndex]
    if not tStartNumber.isdigit():
        ExecLog("invalid start number:"+mString)
        return -1

    mString = mString[tIndex+1:]
    tIndex = mString.find('/')
    if tIndex == -1: 
        ExecLog("can't find /:"+mString)
        return -1
    tEndNumber = mString[:tIndex].strip()
    if not tEndNumber.isdigit():
        ExecLog("invalid end number:"+mString)
        return "error"
    
    tTotal = mString[tIndex+1:].strip()
    if not tEndNumber.isdigit():
        ExecLog("invalid total number:"+mString)
        return -1
    
    if int(tEndNumber) != int(tTotal): return int(tEndNumber)
    else                   : return 0

def find_douban_id(mItem):
    try:
        for a in mItem.find_all('a'):
            #print(a)
            #print(a['href'])
            tDoubanID =  get_id_from_link(a['href'],DOUBAN)
            if tDoubanID.isdigit():
                return tDoubanID
    except Exception as err:
        print(mItem)
        print(err)
        ExecLog("exception at find_douban_id")
        return ""
    return ""

def update_viewed(mOnlyFirstPage=True):

    cookie_dict = {"cookie":site_cookie}
    s = requests.Session()
    s.cookies.update(cookie_dict)

    tUrl = site_url
    while True:
        try:
            res = s.get(tUrl, headers=my_headers)
            soup = BeautifulSoup(res.text,'lxml')
        except Exception as err:
            print(err)
            ExecLog("except at get url")
            return False
        """
        text = open("viewed2.log").read()
        soup = BeautifulSoup(text,'lxml')
        #print(soup)
        """

        try:
            tSubjectNum = soup.find('span',class_="subject-num").get_text()
        except Exception as err:
            print(err)
            print(soup)
            ExecLog("except at find subject-num")
            return False
        #print(num)
        tNextStartNum = find_end_number(tSubjectNum)
        #print(tNextStartNum)

        try:
            tViewed = soup.find('div',class_="grid-view")
            tItems = tViewed.find_all('div',class_="item")
        except Exception as err:
            print(err)
            print(soup)
            ExecLog("except at find grid-view")
            return False
        #print(viewed)
        for item in tItems:
            #print('----------------------------------------')
            #print(item)
            #print('----------------------------------------')
            try:
                tTitle = item.find('em').get_text()
            except Exception as err:
                print(err)
                print(item)
                ExecLog("except at find em")
                return False
            tDoubanID = find_douban_id(item)
            if tDoubanID == "":
                ExecLog("can't find douban_id:"+tTitle)
                continue
            #print("{}:{}".format(tTitle,tDoubanID))

            tReturn = select("select number,copy,dirname,viewed from movies where doubanid=%s",(tDoubanID,))
            if tReturn == None:
                ErrorLog("error exec:select number,copy,dirname,viewed from movies where doubanid="+tDoubanID)
                continue
            elif len(tReturn) == 0:
                ExecLog("no record in movies doubanid={}:{}".format(tDoubanID,tTitle))
                continue
            else:
                for tResult in tReturn:
                    Number = tResult[0]
                    Copy   = tResult[1]
                    DirName= tResult[2]
                    Viewed = tResult[3]
                    if Viewed == 1: 
                        DebugLog("viewed=1,ignore it:"+DirName)
                        continue
                    if update("update movies set viewed=1 where number=%s and copy=%s",(Number,Copy)):
                        ExecLog("set viewd=1:"+DirName)
                    else:
                        ErrorLog("error exec:update movies set viewed=1 where number={} and copy={}".format(Number,Copy))



        if mOnlyFirstPage :  return True
        if tNextStartNum <= 0: return True   
        tNextStartString = 'start='+str(tNextStartNum)
        tUrl = site_url.replace('start=0',tNextStartString)
        print(tUrl)
        time.sleep(10)
        

    return True

if __name__ == '__main__' :
    update_viewed(False)
