#!/usr/bin/python3
# coding=utf-8
from ptsite import *

download_link='https://leaguehd.com/download.php?id=55958&passkey=dfab9bb8e00a9445760abb17ec2fa772'
rss_name = 'LeagueHD'

url_detail = "https://lemonhd.org/details_movie.php?id=195552"
return_code =PTSite.get_id_from_detail(rss_name, url_detail)
print(return_code)


