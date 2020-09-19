#!/usr/bin/python3

import random
from info import *
from database import *

INFO_IGNORE_FILE='data/info_ignore.txt'
info_ignore_list = []

def in_info_ignore(mDoubanID):
    for i in range(len(info_ignore_list)):
        if info_ignore_list[i]['douban_id'] == mDoubanID: return True
    return False

def read_info_ignore():
    if not os.path.isfile(INFO_IGNORE_FILE): print("info ignore file does not exist"); return False

    for line in open(INFO_IGNORE_FILE):
        tDoubanID,tName = line.split('|',1)
        info_ignore_list.append({'douban_id':tDoubanID,'name':tName})
    return True

def check_movie_info():
    #检查movies中的记录，对应info是否存在
    tSelectResult = select("select doubanid,imdbid,name,nation,year,dirname from movies",None)
    for tResult in tSelectResult:
        DoubanID = tResult[0]
        IMDBID = tResult[1]
        Name   = tResult[2]
        Nation = tResult[3]
        Year   = tResult[4]
        DirName  = tResult[5]
        tInfo = Info(DoubanID,IMDBID)

        if not tInfo.select(False):
            print("no record:{}|{}|{}".format(DoubanID,IMDBID,DirName))
            continue

        if not(Name in tInfo.movie_name or tInfo.movie_name in Name):
            print("diff name:{}|{}|{}".format(Name,tInfo.movie_name,DirName))
            continue

        if Nation != tInfo.nation:
            print("diff nation:{}|{}|{}".format(Nation,tInfo.nation,DirName))
            continue

        if abs(Year - tInfo.year) >= 2:
            print("diff year:{}|{}|{}".format(Year,tInfo.year,DirName))
            continue

def check_info():
    #检查info表中有douban_id，但数据不齐全的
    tSelectResult = select("select doubanid,imdbid from info",None)
    i = 0
    for tResult in tSelectResult:
        i += 1
        DoubanID = tResult[0]
        IMDBID = tResult[1]
        tInfo = Info(DoubanID,IMDBID)
        #print('i={}:{}'.format(i,tInfo.movie_name))

        """
        if tInfo.douban_id == '': 
            if tInfo.spider_douban():
                if tInfo.update_or_insert():
                    print("success to update or insert info:"+tInfo.douban_id)
                else:
                    print("failed to update or insert info:"+tInfo.douban_id)
            else:
                print("empty doubanid:{}|{}".format(tInfo.imdb_id,tInfo.movie_name))
            continue
        """
        
        if in_info_ignore(tInfo.douban_id):
            #print("in ignore list:"+tInfo.movie_name)
            continue

        ToBeUpdate = False
        if tInfo.poster == "":
            print("empty poster:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.year == 0:
            print("empty year:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.director == "":
            print("empty director:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.actors == "":
            print("empty actor:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.nation == "":
            print("empty nation:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.genre == "":
            print("empty genre:"+tInfo.movie_name)
            ToBeUpdate = True
        if tInfo.douban_score == "":
            print("empty douban_score:"+tInfo.movie_name)
            ToBeUpdate = True

        #if tInfo.director == "": continue
        director2 = re.sub(u"[\u4e00-\u9f50]+","",tInfo.director) #去掉name中的中文字符
        if tInfo.director != "" and len(director2)  == len(tInfo.director) :
            print("no chinese in director:{}|{}".format(tInfo.movie_name,tInfo.director))
            ToBeUpdate = True

        #if tInfo.actors == "": continue
        actors2 = re.sub(u"[\u4e00-\u9f50]+","",tInfo.actors) #去掉name中的中文字符
        if tInfo.actors != "" and len(actors2)  == len(tInfo.actors) :
            print("no chinese in actor:{}|{}".format(tInfo.movie_name,tInfo.actors))
            ToBeUpdate = True

        if ToBeUpdate == False: continue
        print("begin:"+tInfo.douban_id+'|'+tInfo.movie_name)
        Log(INFO_IGNORE_FILE,tInfo.douban_id+'|'+tInfo.movie_name,time_flag=False)

        if not tInfo.spider_douban():
            print("failed to douban detail:"+tInfo.douban_id)
            continue

        if tInfo.update_or_insert():
            print("success to update or insert info:"+tInfo.douban_id)
        else:
            print("failed to update or insert info:"+tInfo.douban_id)
        
        tSeconds = random.randint(240,600)
        print("sleep {} Seconds:".format(tSeconds))
        time.sleep(tSeconds)


def check_all_id():
    check_id('info')
    check_id('rss')
    check_id('movies')

def check_id(table_name):
    """
    1，检查table表中doubanid 和 imdbid格式的。
    """
    tList = select("select doubanid,imdbid from "+table_name,None)
    print("begin check id of table "+table_name)

    for i in range(len(tList)):
        douban_id = tList[i][0]
        imdb_id   = tList[i][1]

        #检查imdbid并转换.更新转换后的imdbid
        imdb_id   = Info.check_imdb_id(imdb_id)
        if imdb_id != "" and imdb_id != tList[i][1]:
            print("tobe update imdbid:{}|{}".format(imdb_id,tList[i][1]))
            update('update '+table_name+' set imdbid=%s where imdbid=%s',(imdb_id,tList[i][1]))
        #检查doubanid格式是否正确,只打印不更新
        if douban_id != "" and not douban_id.isdigit(): print("doubanid not digit:"+douban_id)
        j = i+1
        while j < len(tList):
            douban_id2 = tList[j][0]
            imdb_id2   = tList[j][1]
            #doubanid相同，但是imdbid不同的
            if douban_id != "" and douban_id2 == douban_id and imdb_id2 != imdb_id:
                #如果一个为空，就把另外一个不为空的更新进去
                if  imdb_id == "" or imdb_id2 == "":
                    update("update "+table_name+' set imdbid=%s where doubanid=%s and imdbid=""',
                            (imdb_id if imdb_id != "" else imdb_id2,douban_id))
                else:
                    #两个不为空，值不相同，打印出来
                    print("sam douban_id,diff imdb_id:{}|{}::{}".format(imdb_id,imdb_id2,douban_id))
            #imdbid相同，但是doubanid不同的
            if imdb_id != "" and imdb_id2 == imdb_id and douban_id2 != douban_id:
                #如果一个为空，就把另外一个不为空的更新进去
                if  douban_id == "" or douban_id2 == "":
                    update("update "+table_name+' set doubanid=%s where imdbid=%s and doubanid=""',
                            (douban_id if douban_id != "" else douban_id2,imdb_id))
                else:
                    #两个不为空，值不相同，打印出来
                    print("same imdb_id,diff douban_id:{}|{}::{}".format(douban_id,douban_id2,imdb_id))
            j += 1 

    """
    tInfoList=[]
    for tSelect in tResult:
        tInfo = Info(douban_id=tSelect[0],imdb_id=tSelect[1])
        tInfoList.append(tInfo)
        if tInfo.imdb_id != "" and len(tInfo.imdb_id) <= 8: print(tInfo.imdb_id)
        if tInfo.imdb_id != "" and not tInfo.imdb_id.startswith("tt"): print(tInfo.imdb_id)
        if tInfo.imdb_id != "" and not tInfo.imdb_id[2:].isdigit(): print(tInfo.imdb_id)
        if len(tInfo.imdb_id) >= 10 and tInfo.imdb_id[2:3] == '0': print(tInfo.imdb_id)

        if tInfo.douban_id != "" and not tInfo.douban_id.isdigit(): print(tInfo.douban_id)

    #check same douban_id, different imdb_id or same imdb_id ,different douban_id
    for i in range(len(tInfoList)):
        j=i+1
        while j < len(tInfoList):
            if tInfoList[i].douban_id != "" and tInfoList[j].douban_id == tInfoList[i].douban_id and tInfoList[j].imdb_id != tInfoList[i].imdb_id:
                print("diff imdb_id:{}|{}::{}".format(tInfoList[i].imdb_id,tInfoList[j].imdb_id,tInfoList[i].douban_id))
            if tInfoList[i].imdb_id != "" and tInfoList[j].imdb_id == tInfoList[i].imdb_id and tInfoList[j].douban_id != tInfoList[i].douban_id:
                print("diff douban_id:{}|{}::{}".format(tInfoList[i].douban_id,tInfoList[j].douban_id,tInfoList[i].imdb_id))
            j += 1 
    """

def check_douban_id():
    """
    检查info表中douban_id为空的情况
    """
    result = select("select name,imdbid from info where doubanid = \"\"",None)
    for select in result:
        movie_name = select[0]
        imdb_id = select[1]
        print("name={}imdbid=:{}".format(movie_name,imdb_id))
        info = Info("",imdb_id)
        info.get_douban_id_by_imdb_id()
        time.sleep(10)
        if info.douban_id == "": print("can't find douban_id:"+movie_name); continue
        print("doubanid="+info.douban_id)
        if info.douban_detail() == OK :
            print("更新info表数据:{}|{}|{}".format(info.movie_name,info.nation,info.douban_id))
            if not info.update(): print("更新info表失败")
        else:
            print("爬取豆瓣信息失败:"+info.douban_id)
        time.sleep(20)

        
if __name__ == '__main__':
    read_info_ignore()
    #check_movie_info()
    #check_info()
    check_all_id()
