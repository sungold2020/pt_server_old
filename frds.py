#!/usr/bin/python3
# coding=utf-8
import requests

myheaders={
    'authority': 'pt.keepfrds.com',
    'method': 'GET',
    'path': '/details.php?id=11284&hit=1',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': 'c_secure_uid=MzEzNDI%3D; c_secure_pass=23911bfa87853213d48cf9968963e4bf; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; _ga=GA1.2.487776809.1582807782; __cfduid=dfb9be8b9ae90ac0ca0f5706d1b6654e71593262434',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
   }
"""   
:authority: pt.keepfrds.com
:method: GET
:path: /details.php?id=11284&hit=1
:scheme: https
accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: zh-CN,zh;q=0.9
cookie: c_secure_uid=MzEzNDI%3D; c_secure_pass=23911bfa87853213d48cf9968963e4bf; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; _ga=GA1.2.487776809.1582807782; __cfduid=dfb9be8b9ae90ac0ca0f5706d1b6654e71593262434; _gid=GA1.2.148578234.1595247439; _gat_gtag_UA_106541394_1=1
referer: https://pt.keepfrds.com/torrents.php
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: same-origin
sec-fetch-user: ?1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36
"""

myheaders={

    'cookie': 'c_secure_uid=MzEzNDI%3D; c_secure_pass=23911bfa87853213d48cf9968963e4bf; c_secure_ssl=eWVhaA%3D%3D; c_secure_tracker_ssl=eWVhaA%3D%3D; c_secure_login=bm9wZQ%3D%3D; _ga=GA1.2.487776809.1582807782; __cfduid=dfb9be8b9ae90ac0ca0f5706d1b6654e71593262434',
    'referer': 'https://pt.keepfrds.com/torrents.php',
    'host': 'pt.keepfrds.com',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
   }
   
res = requests.get('https://pt.keepfrds.com/details.php?id=11284&hit=1',headers=myheaders)
print(res.text)
