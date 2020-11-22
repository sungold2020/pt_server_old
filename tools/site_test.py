#!/usr/bin/python3
# coding=utf-8
from ptsite import *

download_link='https://leaguehd.com/download.php?id=55958&passkey=dfab9bb8e00a9445760abb17ec2fa772'
rss_name = 'LeagueHD'

code,doubanID,imdbID=NexusPage.get_id_from_detail(rss_name,'55958')


