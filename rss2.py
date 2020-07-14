#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import requests
import codecs 
from bs4 import BeautifulSoup
import feedparser

url="https://movie.douban.com/subject/1298038/"
url="https://www.imdb.com/title/tt0125439/"

#url = 'https://www.joyhd.net/torrentrss.php?rows=50&icat=1&ismalldescr=1&isize=1&iuplder=1&linktype=dl&passkey=a770594966a29653632f94dce676f3b8'
#url = 'https://www.hdarea.co/torrentrss.php?rows=10&icat=1&ismalldescr=1&isize=1&iuplder=1&linktype=dl&passkey=cd27426c9894a4c182eb99521afd6f38'
#url='https://pt.soulvoice.club/torrentrss.php?rows=50&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=2e96eb27f1e14173af82b06fecfd767d&inclbookmarked=1'
#url='http://pt.soulvoice.club/torrentrss.php?myrss=1&linktype=dl&uid=91007&passkey=2e96eb27f1e14173af82b06fecfd767d'
url='https://pt.m-team.cc/torrentrss.php?https=1&rows=30&cat401=1&cat419=1&cat420=1&cat421=1&cat439=1&cat403=1&cat402=1&cat435=1&cat438=1&cat404=1&cat409=1&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=7044b36a9057090e36138df761ddfc5d'
url='https://hdsky.me/torrentrss.php?rows=10&tea1=1&tea28=1&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=c8c158c14e1762b0c93c91ab2ddc689a'
url='https://www.beitai.pt/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=e193420544db01e767e2a214f30ec049&inclbookmarked=1'
url='https://pt.keepfrds.com/torrentrss.php?rows=10&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=97f4eab2ad32ebf39ee4889f6328800b'
url='https://leaguehd.com/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=dfab9bb8e00a9445760abb17ec2fa772&inclbookmarked=1'

url='https://ptsbao.club/pushrss.php?pushkey=HvBtGW1jKCijeZMC7IPOkJaOweULzAwK2nffSx3Akw3Jb-fL0ZgHEhNVONhMiEmHD_lHAR4BwM5FDMvGRRgIhuB'
url='http://pthome.net/torrentrss.php?myrss=1&linktype=dl&uid=116626&passkey=c8b0815aa8bf6f1502260a11f8ed2ed7'
url='http://avgv.cc/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=9a269ba45540e516cbf15ebf6dd815b8&inclbookmarked=1'
url='http://pt.soulvoice.club/torrentrss.php?myrss=1&linktype=dl&uid=91007&passkey=2e96eb27f1e14173af82b06fecfd767d'
url='https://pt.soulvoice.club/torrentrss.php?rows=10&icat=1&ismalldescr=1&linktype=dl&passkey=2e96eb27f1e14173af82b06fecfd767d&inclbookmarked=1'
url='https://www.joyhd.net/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=a770594966a29653632f94dce676f3b8&inclbookmarked=1'
url='https://www.beitai.pt/torrentrss.php?rows=20&icat=1&ismalldescr=1&isize=1&linktype=dl&passkey=e193420544db01e767e2a214f30ec049&inclbookmarked=1'
headers = {    
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'}
"""
page = requests.get(url, headers=headers)
page.encoding = 'utf-8'
page_content = page.text
f = codecs.open('news.txt', 'w', 'utf-8')
f.write(page_content)
soup = BeautifulSoup(page_content, 'lxml-xml')
news = soup.select('rss > channel > item')
for i in range(len(news)):
    print(news[i].title.string)
    print(news[i].description.string)
    print(news[i].link.string)
    print(news[i].guid.string)
    print(news[i].enclosure.get('url'))
    print(news[i])
f.close()
"""
print(url)

d=feedparser.parse(url)
print(d)
#print(d)
for t in d.entries :
    Title = t.title
    ID    = t.id
    Detail = t.links[0].href
    DownloadLink = t.links[1].href
    print(Title)
    print(ID)
    print(Detail)
    print(DownloadLink)
    print(t)
    try:
        txt=BeautifulSoup(t.summary,'lxml')
        print(txt.get_text())
    except KeyError:
        print("no summary")
    except Exception as err:
        print(err)

    DownloadLink = t.links[1].href
    DoubanScore = ""
    DoubanLink = ""
    IMDBLink = ""
    IMDBScore = ""
    break
        
#print (d)
#print (d.feed.subtitle)
#print (len(d.entries))
#print (d.entries[0])
