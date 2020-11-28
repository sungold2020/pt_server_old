#!/usr/bin/python3
# coding=utf-8
import os
import re
import sys
import shutil
import datetime
from pathlib import Path
from moviepy.editor import VideoFileClip
import torrentool.api

from database import *
from info import *
from log import *

SUCCESS           = 1    
SRC_NOT_DIR       = -1
DEST_NOT_DIR      = -2
DEPTH_ERROR       = -3
UNKNOWN_FILE_TYPE = -4
FAILED_MOVE       = -5
FAILED_RMDIR      = -6
TABLE_ERROR       = -7

ENCODE       = 0
BLUE_RAY     = 1

class Movie:
    """
    一部电影存储在一个目录中，目录名带有电影的编号，名称，格式等信息
    """

    #0表示测试，不执行修改，1表示执行修改
    ToBeExecDirName = True     # DirName名称
    ToBeExecRmdir   = False     # 从子文件夹将内容提上来 删除空子目录

    def __init__(self,dir_path="",dir_name="",disk=""):
        self.dir_name = dir_name   # 目录名称
        self.disk     = disk       # 磁盘名 例如sg3t-2
        self.dir_path = dir_path   # 所在物理路径

        self.number = -1           # -1:error
        self.copy = 0              # 0 表示正本，其他表示不同版本1:3D版，2:加长版
        self.nation = ""           #
        self.type = MOVIE          # 0:Movie 1:TV 2:Record
        self.name = ""             #
        self.min = 0
        self.format_type = ENCODE  # 文件格式类型，0：重编码，1：蓝光原盘 
        
        # 从格式中获取的信息
        self.radio = ""            # 分辨率
        self.version = ""          # 版本，例如CC，DC
        self.nation_version = ""   # 国家版本，如韩版，日版:JPN
        self.special = ""          # 特别说明，例如rerip
        self.source = ""           # 来源，如Blu-Ray，Web-DL
        self.compress = ""         # 压缩算法,如x264
        self.audio = ""            # 音频格式，如DTS
        self.track = ""            # 音轨，如2audio 
        self.bit = ""              # 色彩精度，10bit,8bit
        self.HDR = ""              # HDR
        self.zip_group = ""        # 压缩组
        
        self._total_size = 0       # 电影文件大小，unit:M 取值:torrent.total_size / (1024*1024)
        self.deleted  = 0
        self._douban_id = ""       #
        self._imdb_id = ""         # 
        self.update_time = ""
        self.check_time = ""

        self.checked = 1      #

        self.english_name = ""     # 英文片名（也可能是其他语种）
        self.year = 0              # 年份

        # 目录内容组成部分
        self.jpg = 0           #是否有海报图片 
        self.nfo = 0           #是否有nfo文件
        self.number_of_SP = 0    #花絮等的数量
        self.number_of_video = 0 #不包含SP开头的视频文件，可能的几种情况
        # 0 :没有视频文件 
        # -1:有多个视频文件但不在定义的范围内 
        # >1:表示多个合集，可能发生的情况：
        #    1) 在纪录片和电视剧目录下，有效
        #    2) Part1/2,Disk1/2，任何两个文件名之间差别仅存在1个且为数字，有效
        #    3) 其他情况下，把它置为-1
        self.video_files =[] # 保存video文件名在数组中
        self.sample_video = ""  #
        
        self.hash = ""
        self.torrent_file = ""
        self.resume_file  = ""
        self.download_link = ""
        self.IsError = 0       # 检查完以后是否有错误


        self.collection = 0    #是否为合集
        self.number2 = 0       #合集下的第二个数字
        self.sub_movie = []     #合集下的对象
        self.sub_movie_count = 0 #合集下的目录数量

        self.format_str = "" 
        self.dir_name_todo = False   #目录名称是否要修改        

    @staticmethod
    def from_db(number=-1, copy=-1, total_size=0):
        db_movie = Movie()
        db_movie.number     = number
        db_movie.copy       = copy
        db_movie.total_size = total_size
        if db_movie.select():
            return db_movie
        return None

    @property
    def douban_id(self):
        return self._douban_id
    @douban_id.setter
    def douban_id(self,douban_id):
        douban_id = douban_id.strip()
        if douban_id != "" and not douban_id.isdigit(): ErrorLog("invalid doubanid:"+douban_id); return 
        self._douban_id = douban_id

    @property
    def imdb_id(self):
        return self._imdb_id
    @imdb_id.setter
    def imdb_id(self,imdb_id):
        self._imdb_id = Info.check_imdb_id(imdb_id)

    @property
    def total_size(self):
        if self._total_size > 0: return self._total_size
        if not self.get_torrent(): 
            return 0
        try:
            torrent_info = torrentool.api.Torrent.from_file(self.torrent_file)
            self._total_size = int(torrent_info.total_size / (1024*1024))
        except Exception as err:
            print(err)
        return self._total_size
    @total_size.setter
    def total_size(self, total_size):
        self._total_size = total_size

    def check_dir_name(self):
        """
        #检查该目录名称格式是否合法，并分解出各元素,如果缺少Min或者format则置位self.dir_name_todo = True
        # 正确的几种格式如下(包括合集)：
        # "Number-nation-name XXXMin Format"            完整
        # "Number-nation-name Format"                   缺少Min，待补充
        # "Number-nation-name XXXMin"                   缺少format，待补充
        # "Number-nation-name"                          缺少Min和format
        # "Number-nation-纪录片/电视剧-name Format"     完整
        # "Number-nation-纪录片/电视剧-name"            缺少格式
        # "Number-copy-nation-name ...."
       
        # 合集的正确格式
        # "Number-Number-nation-name Format"
        # "Number-Number-nation-name"
        # 合集下标记IsCollection=1
       
        # "name可以是多个名称，中间加-作为连接符，例如兄弟连-全10集
       
        """
       
        # 找出Number
        FindIndex = self.dir_name.find("-")
        if FindIndex == -1 :  
            ErrorLog ("Error number:" + self.dir_name +"::") 
            self.IsError = 1 ;  return False
        NumberStr = self.dir_name[0:FindIndex]   
        Lest = self.dir_name[FindIndex+1:]       
        if not(NumberStr.isdigit())  :#不是数字的话。
            ErrorLog ("invld Number1:"+self.dir_name +"::"+NumberStr) 
            self.IsError = 1 ;  return False
        self.number = int(NumberStr)
        #加入NumberStr小于4，则需要补零，至self.dir_name_todo = 1，留给Renamedir_name函数去补零
        if len(NumberStr) < 4: self.dir_name_todo = True
        
        #继续找nation或者Copy或者Number2
        FindIndex = Lest.find("-")
        if FindIndex == -1 :  
            ErrorLog ("Error nation:" + self.dir_name +"::")
            self.IsError = 1 ;  return False
        self.nation = Lest[0:FindIndex]
        Lest = Lest[FindIndex+1:]
        #如果nation是数字:
        #1、是一个0-9的数字，则代表copy
        #2、是长度>=4的数字字符，则说明是合集，先找出Number2，然后才是nation
        if self.nation.isdigit() : 
            if len(self.nation) == 1:            #copy
                self.copy = int(self.nation)
            elif len(self.nation) >= 4:          #合集
                self.number2 = int(self.nation)
                if self.number2 <= self.number : #合集的第二个数字应该大于第一个
                    ErrorLog ("Error number2:"+self.dir_name+"::"+self.nation)
                    self.IsError = 1 ; return False
                self.collection = 1
            else:
                ErrorLog ("4- number2:"+self.dir_name+"::"+self.nation)
                self.IsError = 1 ; return False
                
            # 继续找nation
            FindIndex = Lest.find("-")
            if FindIndex == -1 :
                ErrorLog ("Error nation in collection:" + self.dir_name + "::" + Lest) 
                self.IsError = 1 ; return False
            self.nation = Lest[0:FindIndex]
            Lest = Lest[FindIndex+1:]
            
        #判断nation长度
        if len(self.nation) > 5 :
            ErrorLog ("5+length nation:" + self.dir_name + "::" + Lest) 
            self.IsError = 1 ; return False
            
        # 如果前三个字符是电视剧或者纪录片
        if Lest[0:3] == "纪录片" :
            self.type = RECORD
        elif Lest[0:3] == "电视剧" :
            self.type = TV
        else :
            self.type = MOVIE
        if self.type != MOVIE:   #电视剧或者纪录片
            if Lest[3:4] != "-" :
                ErrorLog ("Error：not - :"+self.dir_name)
                self.IsError = 1 ; return False
            Lest = Lest[4:]
            
        #继续找name
        FindIndex = Lest.find(" ")
        if FindIndex == -1 :  #说明name后面就空了，没有min和Format
            self.name = Lest
            return True    
        self.name = Lest[0:FindIndex]
        Lest = Lest[FindIndex+1:]
        
        #继续找min
        FindIndex = Lest.find("Min")
        if FindIndex == -1 :
            #movie_log ("No Min:"+self.dir_name)
            self.format_str = Lest
            return True
        else:
            #Min后面没有了format
            if len(Lest) == FindIndex+3 :
                self.min = int(Lest[0:FindIndex].lstrip())
                #movie_log("no format after Min:"+self.dir_name+"::"+str(self.min))
                return True
            #Min后的第一个字符是不是空格，如果不是表示Min可能是格式中的字符，例如Mind
            elif Lest[FindIndex+3:FindIndex+4] != ' ':
                #movie_log ("Min之后不是空格:"+Lest[FindIndex+3:FindIndex+4]+"::"+self.dir_name)
                self.format_str = Lest
            else :
                MinStr = Lest[0:FindIndex].lstrip() #Min之前的字符为MinStr,并去掉左边的空格符
                if not MinStr.isdigit() :
                    ErrorLog ("Invalid Min:"+self.dir_name+"::"+MinStr)
                    self.IsError = 1 ; return False
                self.min = int(MinStr)
                self.format_str = Lest[FindIndex+4:]
        """
        if len(self.format_str) < 15:
            ErrorLog ("15- Format:"+self.dir_name+self.format_str)
            self.IsError = 1; return False
        """ 
        return True
    #end def check_dir_name    
        
    def check_dir_cont(self) :
        '''
        前置条件:
        1、执行过check_dir_name，因为需要调用self.IsCollection
        2、不能是合集，如果是返回错误。
        
        检查目录下的内容，可能有效的几种情况:
        1、有且只有一个子目录，且子目录下不再有目录。则把子目录内容提取到上级目录。
        2、有srt/ info/ SP/的子目录（其他目录非法，报错）
        3、没有子目录
        
        1、type为电视剧/纪录片下，目录中可以有多个视频文件
        2、type为0，目录中只有一个视频文件
        3、type为0，目录中有多个视频文件，但视频文件差别只有一个字符（且为数字），例如Disk1，Disk2
        4、忽略掉SP开头的视频文件（花絮等）
        5、发现有sample字样的视频文件，仅记录错误日志和标记在SampleVideo，待手工处理。以免误删
        
        6、有JPG海报文件，则拷贝poster/cover.jpg，无则标记Jpg=0，不影响检查和返回值
        '''

        if self.collection == 1 :
            ErrorLog("Error:it is collection in CheckCont:"+self.dir_name)
            self.IsError =1; return False
            
        NumberOfSubDir = 0
        NumberOfFile = 0
        CoverJpg = 0
        PostJpg = 0
        SubDirName = ""      #仅当NumberOfSubDir=1才有意义
        JpgFileName = ""
        for File in os.listdir(os.path.join(self.dir_path,self.dir_name)):
            FullPathFile = os.path.join(os.path.join(self.dir_path,self.dir_name),File)
            if os.path.isdir(FullPathFile):
                if File[0:2] == "SP" or File[0:3] == "srt" or File[0:3] == "inf" or File[0:4] == "info" : # 忽略掉特殊文件夹
                    movie_log ("it is SP/srt/info DIR:"+File)
                    continue
                if os.path.islink(FullPathFile) :
                    movie_log ("it is a link:"+self.dir_name)
                    continue 
                if File == "BDMV": 
                    self.format_type = BLUE_RAY
                    continue

                SubDirName = FullPathFile 
                NumberOfSubDir += 1
            elif os.path.isfile(FullPathFile):
                NumberOfFile += 1
                #视频文件
                if File[-3:] == "avi" or File[-3:] == "mkv" or File[-2:] == "ts" or File[-3:] == "mp4" :
                    if File[0:2] == "SP" :
                        movie_log ("find SP video:"+File)
                        self.number_of_SP += 1
                    elif re.search("sample",File,re.I):
                        movie_log ("find sample video:"+File+"::"+self.dir_name)
                        ErrorLog("sample video:"+File+"::"+self.dir_name)  #仅记录，不做处理，待手工处理
                        self.sample_video = File 
                    else:
                        self.number_of_video += 1
                        self.video_files.append(File)
                #jpg海报文件
                elif File[-3:] == "jpg" :
                    if File == "cover.jpg":
                        CoverJpg = 1
                    elif File == "poster.jpg" :
                        PostJpg = 1
                    else :
                        JpgFileName = File
                #nfo
                elif File[-3:] == "nfo" :
                    self.nfo = 1
                #torrent
                elif File[-6:] == 'resume' or File[-7:] == 'torrent' or File == 'download.txt':
                    pass
                elif File.endswith(".iso"):
                    self.format_type = BLUE_RAY
                else:
                    ExecLog ("other type file"+File)
            else:
                ErrorLog("not file or dir :"+FullPathFile)
                self.IsError = 1; return False
                
        if NumberOfSubDir == 1:   #除了srt/info/SP/之外有一个子目录
            if NumberOfFile == 0 :#除了一个子目录外没有其他文件
                SrcDir  = os.path.join(os.path.join(self.dir_path,self.dir_name),SubDirName)
                DestDir = os.path.join(self.dir_path,self.dir_name)
                if Movie.ToBeExecRmdir == True :
                    if MoveDirFile(SrcDir,DestDir) == SUCCESS:
                        ExecLog("mv "+SrcDir+" "+DestDir)
                        return self.check_dir_cont()   #已经移动文件夹成功，再重新检查
                    else:
                        ErrorLog("failed mv "+SrcDir+" "+DestDir)
                        self.IsError = 1; return False                       
                else:
                    movie_log("todo mv "+SrcDir+" "+DestDir)
                    self.IsError = 1; return False
            else:  #试图删除这个空的子目录，如果不成功，说明不是空的，报错
                try :
                    os.rmdir(SubDirName)
                    ExecLog("rmdir "+SubDirName)
                except:
                    ErrorLog("one not empty subdir:"+SubDirName)
                    self.IsError = 1; return False
        elif NumberOfSubDir > 1:
            ErrorLog("1+ subdir:"+self.dir_name)
            self.IsError = 1; return False
        else :
            movie_log ("no subdir"+self.dir_name)
        
        #检查海报
        CurrentPath = os.path.join(self.dir_path,self.dir_name)
        if PostJpg == 1 :
            if CoverJpg == 0:
                try :
                    SrcFileName  = os.path.join(CurrentPath,"poster.jpg")
                    DestFileName = os.path.join(CurrentPath,"cover.jpg")
                    shutil.copyfile(SrcFileName,DestFileName)
                    ExecLog("cp poster.jpg cover.jpg in"+self.dir_name)
                    self.jpg = 1
                except:
                    ErrorLog("failed cp poster.jpg in"+self.dir_name)
                    self.IsError = 1; return False
            else:
                self.jpg = 1
        elif CoverJpg == 1:   #没有poster.jpg但是有cover.jpg 
            try :
                SrcFileName  = os.path.join(CurrentPath,"cover.jpg")
                DestFileName = os.path.join(CurrentPath,"poster.jpg")
                shutil.copyfile(SrcFileName,DestFileName)
                ExecLog("cp cover.jpg in"+self.dir_name)
                self.jpg = 1
            except:
                ErrorLog("failed cp cover.jpg in"+self.dir_name)
                movie_log("failed cp cover.jpg in"+self.dir_name)
                movie_log(SrcFileName)
                movie_log (DestFileName)
                self.IsError = 1; return False
        elif JpgFileName != "" : #但是还有其他jpg文件
            try :
                SrcFileName  = os.path.join(CurrentPath,JpgFileName)
                DestFileName = os.path.join(CurrentPath,"poster.jpg")
                movie_log ("To CP:"+SrcFileName)
                movie_log ("      "+DestFileName)
                shutil.copyfile(SrcFileName,DestFileName)
                ExecLog("cp "+JpgFileName+" poster.jpg in"+self.dir_name)
                DestFileName = os.path.join(CurrentPath,"cover.jpg")
                shutil.copyfile(SrcFileName,DestFileName)
                movie_log ("      "+DestFileName)
                ExecLog("cp "+JpgFileName+" cover.jpg in"+self.dir_name)
                self.jpg = 1
            except:
                ErrorLog("failed cp "+JpgFileName+" in"+self.dir_name)
                self.IsError = 1; return False
        else:
            ErrorLog("no jpg file:"+self.dir_name)
            self.jpg = 0   #标记，但不返回，不影响后续检查操作
        #print("check jpg complete")
        
        # 检查视频文件
        if self.format_type == ENCODE:
            if self.number_of_video == 0:
                ErrorLog("no video in"+self.dir_name)
                self.IsError = 1 ; return False
            elif self.number_of_video == 1:
                #print("check video complete")
                return True
            else : #>=2忽略SP/sample外，还有多个视频文件，则需要进一步分析
                if self.type == RECORD or self.type == TV : #电视剧/纪录片
                    pass
                else:
                    #比较多个video名的差别，
                    #如果长度一致，仅有一个字符的差别，且这个字符是数字。则OK，否则报错
                    #先以第一个VideoFileName为比较对象，后面逐个VideoFileName和它比较
                    length = len(self.video_files[0])
                    for i in range(self.number_of_video):
                        if len(self.video_files[i]) != length :
                            ErrorLog("diff len video:"+self.dir_name)
                            movie_log ("diff len video:"+self.dir_name)
                            movie_log ("  1:"+self.video_files[0])
                            movie_log ("  2:"+self.video_files[i])
                            #self.number_of_video = -1
                            #self.IsError = 1 ; return False
        return True
    #end def check_dir_cont    

    def get_runtime(self):
        """
        获取video的时长，多个video就累加。
        前置条件：执行过check_dir_cont，已经获取了self.video_files
        """
        if self.number_of_video <= 0 :
            movie_log ("no video file:"+self.dir_name)
            return 0
        if self.type != MOVIE:
            return 0

        tMin = 0
        for i in range(self.number_of_video):
            Path = os.path.join(self.dir_path,self.dir_name)
            movie_file = os.path.join(Path,self.video_files[i])
            try:
                clip = VideoFileClip(movie_file)
                tMin += int(clip.duration/60)
                clip.reader.close()
                clip.audio.reader.close_proc()
            except Exception as err:
                print(err)
                ExecLog("error:get runtime:"+self.dir_name)
                return 0
        return tMin

    ''' 
    def runtime_from_mkv(self):
        """
        前置条件：
        1、已经执行过check_dir_cont
        2、有效的NumberOfViedeo，而且是MKV文件（其他格式暂不支持）
           如果是多个有效的Mkv，则叠加Min
        
        返回的是分钟数，如果为0表示错误
        """

        if self.number_of_video == 0 :
            #movie_log ("not 1 video:"+self.dir_name)
            return 0
        if self.type != MOVIE:
            return 0

        tMin = 0
        for i in range(self.number_of_video):
            if (self.video_files[i])[-3:] != "mkv" :
                #movie_log ("not mkvfile:"+self.dir_name)
                return 0

            Path = os.path.join(self.dir_path,self.dir_name)
            MkvName = os.path.join(Path,self.video_files[i])
            RunTimeStr='mkvinfo --ui-language en_US "'+MkvName+'" | grep Duration'
            movie_log(RunTimeStr)
            #movie_log (RunTimeStr)
            Line = os.popen(RunTimeStr).read()
            #movie_log (Line[:24])
            Hour=Line[14:16]
            Min=Line[17:19]
            #movie_log (Hour+" "+Min)
            if not ( Hour.isdigit() and Min.isdigit() ):
                #movie_log ("Hour or Min isn't digit"+Hour+":"+Min)
                return 0

            MinNumber = int(Hour)*60 + int(Min)
            #movie_log ("Min="+str(MinNumber))
            tMin += MinNumber
        return tMin
    '''
    
    def format_from_video_file(self):
        '''
        从video_file中提取format，赋值到self.format_str
        前置条件：
        1、已经执行过check_dir_cont
        2、有且只有一个有效的视频文件NumberOfVideo == 1
        
        成功返回True，否则返回False
        '''  
        
        if not self.number_of_video == 1 :
            movie_log ("2+Video,don't know how to find format from video")
            return False
        
        FileName = self.video_files[0]
        Length = len(FileName)
        if FileName[-3:] == "mkv" or FileName[-3:] == "avi" or FileName[-3:] == "mp4":
            self.format_str = FileName[:Length-4]
            return 1
        elif FileName[-2:] == "ts":
            self.format_str = FileName[:Length-3]
            return True
        else:
            return False
    #end def format_from_video_file    
    
    def rename_dir_name(self):
        """
        前置条件：
        1、正确执行过check_dir_name,即已经把DirName分解出各元素
        2、正确执行过check_dir_cont，即该目录下有正确的视频文件，因为需要通过视频文件获取Min和Format
        
        如果DirName信息不准确或者不完整的话，尝试补充完成并修改
        一、持续检查各个元素，如果缺少尝试补充:
        1、元素出现错误，并且无法补充完成，记录错误日志并返回0
        2、无错误，也不需要补充修改，dir_name_todo=0，返回1
        3、无错误，补充修改完成，DirNameTodo = 1 
        二、DirNameTodo =1，尝试修改
        1、如果ToDoExecDirName=1，则进行修改:
            1）修改成功，返回1，并记录执行日志
            2）修改错误，返回0，并记录错误日志
        2、否则，记录执行日志（ToDo）
        """

        #movie_log("begin rename_dir_name")
        if self.collection == 1 :
            ErrorLog("Error:it is collection in rename_dir_name:"+self.dir_name)
            self.IsError = 1; return False
        if self.number <= 0 or self.number >= 10000 :
            ErrorLog("ErrorNumber:"+self.dir_name+"::"+str(self.number))
            self.IsError = 1 ; return False
        if  len(self.nation) ==0 or len(self.nation) >= 8 :
            ErrorLog("8+nation :"+self.dir_name+"::"+self.nation )
            self.IsError = 1; return False
        if len (self.name) == 0 or len(self.name) >= 20 :
            ErrorLog("20+name :"+self.dir_name+"::"+self.name )
            self.IsError = 1; return False
        
        #movie_log (str(self.min))
        MinFromMkv = self.get_runtime()
        #movie_log (str(MinFromMkv))
        if self.min == 0 and self.type == MOVIE:
            if MinFromMkv == 0:
                ErrorLog("not Found Min:"+self.dir_name)
                self.IsError = 1 ; return False
            else:
                self.min = MinFromMkv ; self.dir_name_todo = True
        if self.type == MOVIE and MinFromMkv != 0 and abs(self.min-MinFromMkv) >= 2:
            movie_log("Min-MinFromMkv >= 2:{}|{}".format(self.min,MinFromMkv))
            self.min = MinFromMkv ; self.dir_name_todo = True
            
        self.format_str = self.format_str.strip()  #去掉前后空格
        movie_log("Current formatstr;"+self.format_str)
        if len(self.format_str) == 0:
            #从video 文件名里提取出格式文件
            if self.format_from_video_file() == False:
                ErrorLog("not found Format:"+self.dir_name)
                self.IsError = 1; return False
            movie_log("find Format:"+self.format_str)
            self.dir_name_todo = True
        elif len(self.format_str) <= 10:
            ErrorLog("10-Format:"+self.dir_name+"::"+self.format_str)
            self.IsError = 1; return False
        else:
            movie_log ("correct format"+self.format_str)
        
        #如果TODO=0，说明dir_name不需要修改
        if self.dir_name_todo == False :
            movie_log ("Correct dir_name:"+self.dir_name)
            return True

        SourceDir = os.path.join(self.dir_path,self.dir_name)
        NumberStr = (str(self.number)).zfill(4)
        if self.copy > 0:
            NumberStr = NumberStr + "-" + str(self.copy)
        
        if self.type == MOVIE:
            DestDirName = NumberStr+"-"+self.nation+"-"+self.name+" "+str(self.min)+"Min "+self.format_str
        elif self.type == TV: 
            DestDirName = NumberStr+"-"+self.nation+"-电视剧-"+self.name+" "+self.format_str
        elif self.type == RECORD:
            DestDirName = NumberStr+"-"+self.nation+"-纪录片-"+self.name+" "+self.format_str
        else:
            ErrorLog("Error type:"+self.dir_name+"::"+int(self.type))
            self.IsError = 1; return False
            
        DestDir = os.path.join(self.dir_path,DestDirName)
        
        movie_log("begin rename dirname:")
        if Movie.ToBeExecDirName == True:
            try:
                os.rename(SourceDir,DestDir)
                ExecLog("mv "+self.dir_name)
                ExecLog("   "+DestDirName)
                movie_log ("rename success")
                self.dir_name = DestDirName
                return True
            except:
                ErrorLog("mv failed:"+self.dir_name)
                ErrorLog("          "+DestDirName)
                movie_log ("Mv failed:"+SourceDir)
                movie_log ("          "+DestDir)
                self.IsError = 1 ; return False
        else:
            movie_log("ToDo mv "+self.dir_name)
            movie_log("        "+DestDirName)
            return True
    #end def rename_dir_name
    
    def check_info(self):
        """
        功能：检查movie的doubanid和imdbid相关信息
        1、获取doubanid和imdbid，如果失败，返回False
        2、从info表检索影片名，nation等必要信息，
            A,检索出必要信息，比较info中的name,nation和movie中的是否一致, 不一致，返回False，否则返回True
            B,未检索出必要信息，则跳转3
        3、如果info表未检索出信息，则尝试重新爬取,失败，返回False
        4、下载poster及更新info表
        前置条件：必须先调用check_dir_name获取了movie的基本信息(number,nation,name等)
        """
        #1、获取id，从movies表中查询，或者获取hash，然后从rss中获取id
        if self.imdb_id == "" and self.douban_id == "": 
            if self.get_id_from_table() == False:
                movie_log("empty imdb_id and douban_id in:"+self.dir_name)
                if self.get_id_from_rss():
                    self.update_id()
                else:
                    return False

        #2、检索info表获取必要信息，并比较
        tInfo = Info(self.douban_id,self.imdb_id)
        if tInfo.movie_name != "" and (tInfo.director != "" or tInfo.actors != "") and tInfo.nation == "":
            #比较影片名是否一致
            if not(tInfo.movie_name in self.name or self.name in tInfo.movie_name):
                movie_log(f"name is diff:{self.name}|{tInfo.movie_name}")
                return False
            return True
        #3、重新爬取影片信息，
        tInfo.douban_status = RETRY
        if tInfo.spider_douban() != OK :
            ExecLog("failed to spider_douban:"+self.dir_name)
            return False

        #4、下载poster及更新info表
        tCurrentPath = os.path.join(self.dir_path,self.dir_name)
        if not os.path.isfile(os.path.join(tCurrentPath,'poster.jpg')):
            tInfo.download_poster(tCurrentPath)
        return tInfo.update_or_insert()
    
    def check_movie(self):
        '''
        用于checkmovie.py调用，完整检查目录。内容，等信息
        '''
        
        #1、检查dirname，获取number,copy,name,nation,min,format等
        if self.check_dir_name() == False :
            ErrorLog("failed check_dir_name:"+self.dir_name)
            self.IsError = 1
            return False
        
        #从dirname获取是否collection
        if self.collection == 1:
            movie_log ("Begin collection"+self.dir_name)
            SubDirPath = os.path.join(self.dir_path,self.dir_name)
            for File in os.listdir(SubDirPath):
                FullPathFile = os.path.join(SubDirPath,File)
                if os.path.isdir(FullPathFile):
                    self.sub_movie.append(Movie(SubDirPath,File,self.disk))
                    if self.sub_movie[-1].check_movie() == False:
                        ErrorLog(f"check error:{FullPathFile}")
                        return False
                    self.sub_movie_count += 1
            movie_log ("End collection"+self.dir_name)
            if self.sub_movie_count > 0 :
                return True
            else:
                ErrorLog ("empty collection:"+self.dir_name)
                self.IsError = 1 ; return False
        #end if self.collection == 1
        
        #2、检查format中的格式信息
        if self.split_format() == 0:
            ErrorLog("split_format:"+self.dir_name)
            self.IsError = 1
            #return 0  只记录错误，不返回

        #3、检查id和info信息
        if self.check_info() == False:
            ErrorLog("failed check_info:"+self.dir_name)
            self.IsError = 1
            return False

        #4、检查dir中内容
        if self.check_dir_cont() == False :
            ErrorLog("failed check_dir_cont:"+self.dir_name)
            self.IsError = 1
            return False
            
        #5、如果dirname中,min，format格式不全，补充完整后更新dirname
        if self.rename_dir_name() == False :
            ErrorLog("failed rename_dir_name:"+self.dir_name)
            self.IsError = 1
            return False
        
        #6、更新movie表信息
        if self.check_table() != SUCCESS:
            ErrorLog("check_table:"+self.dir_name)
            self.IsError = 1; return False
        return True
    #end def check_movie

    def save_movie(self):
        '''
        用于ptserver进行保存电影的入口，非必要性错误仅提示
        '''
        
        if self.check_dir_name() == False :
            ErrorLog("failed check_dir_name:"+self.dir_name)
            self.IsError = 1
            return False
        
        if self.split_format() == 0:
            ErrorLog("split_format:"+self.dir_name)
            self.IsError = 1

        if self.check_dir_cont() == False :
            ErrorLog("failed check_dir_cont:"+self.dir_name)
            self.IsError = 1
            
        if self.rename_dir_name() == False :
            ErrorLog("failed rename_dir_name:"+self.dir_name)
            self.IsError = 1
        
        if self.check_table() != SUCCESS:
            ErrorLog("check_table:"+self.dir_name)
            self.IsError = 1; return 0
        return 1
    #end def check_movie

    
    def split_format(self):
        '''
        对Format进行分析，提取年份，分辨率，压缩算法等
        前置条件：
        check_dir_name必须已经执行，FormatStr已经获取
        '''

        self.format_str = self.format_str.strip()
        if len(self.format_str) == 0 :
            ErrorLog ("no format:"+self.dir_name)
            self.IsError = 1; return 0

        #尝试进行空格分割
        #SplitSign = ' '
        FormatList = (self.format_str).split()
        if len(FormatList) < 3:
            #再尝试进行'.'分割
            FormatList = (self.format_str).split('.')
            if len(FormatList) < 3:
                ErrorLog("3- format:"+self.format_str)
                self.IsError = 1; return 0
            #else :
            #SplitSign = '.'

        #处理最后一个group，通常是XXX-Group格式
        tStr = FormatList[-1]
        tIndex = tStr.rfind('-')
        if tIndex > 0:
            FormatList[-1] = tStr[:tIndex]
            self.zip_group = tStr[tIndex+1:]
        
        NumberOfElement=0  #找到了几个关键字
        LastIndex = -1     #找到关键字后要标记出它在FormatList中的索引
        FormatSign = []    #对应FormatList[]的标志位，0表示未识别，1表示已识别
        #beginfrom 1,0 must be englishname
        i=1 ; FormatSign.append(0)
        while i < len(FormatList) :
            movie_log ("FormatList:i="+str(i)+"::"+FormatList[i])
            TempStr = FormatList[i].lower()
            TempStr = TempStr.replace(' ','')  #删除空格并把它全部转换为小写，便于比较
            FormatSign.append(0)
            
            #年份：
            if (TempStr.isdigit() and int(TempStr) > 1900 and int(TempStr) <= int(datetime.datetime.now().year)):
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.year = int(FormatList[i])
                movie_log ("find Year:"+str(self.year)+"i="+str(i))
            #版本
            elif TempStr == "cc" or \
                 TempStr == "dc" or \
                 TempStr == "extended" or \
                 TempStr == "open-matte" or \
                 TempStr == "the-final-cut" or\
                 TempStr == "uncut" or\
                 TempStr == "unrated" or \
                 TempStr == "complete" or\
                 TempStr == "re-grade" or\
                 TempStr == "cut":
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                if self.version == "": self.version = FormatList[i]
                else:                  self.version += '-'+FormatList[i]
                movie_log ("find Version:"+self.version+"i="+str(i))
            #国家版本
            elif TempStr.upper() == "JPN" or \
                 TempStr.upper() == "GBR" or \
                 TempStr.upper() == "KOR" or \
                 TempStr.upper() == "ESP" or \
                 TempStr.upper() == "USA" or \
                 TempStr.upper() == "NLD" or \
                 TempStr.upper() == "FRA" or \
                 TempStr.upper() == "TW" or \
                 TempStr.upper() == "BFI" or \
                 TempStr.upper() == "TOHO" or \
                 TempStr.upper() == "US" or \
                 TempStr.upper() == "HK":
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.nation_version = FormatList[i]
                movie_log ("find nation_version:"+self.nation_version+"i="+str(i))
            #特别说明，例如rerip
            elif TempStr == "rerip" or \
                 TempStr == "remastered" or\
                 TempStr == "repack":
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.special = FormatList[i]
                movie_log ("find special:"+self.special+"i="+str(i))
            #分辨率
            elif TempStr == "720p" or \
                 TempStr == "1080p" or \
                 TempStr == "2160p" or \
                 TempStr == "1080i" or \
                 TempStr.lower() == "4k" or \
                 TempStr.lower() == "60fps" or \
                 re.match("[0-9][0-9][0-9][0-9]x[0-9][0-9][0-9]p",TempStr) is not None or \
                 re.match("[0-9][0-9][0-9][0-9]x[0-9][0-9][0-9][0-9]p",TempStr) is not None:
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                if self.radio == "": self.radio = FormatList[i]
                else: self.radio += '.'+FormatList[i]
                movie_log ("find Radio:"+self.radio+"i="+str(i))
            #ignore 2d
            elif TempStr == "2d":   
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                movie_log ("ignore 2d:"+"i="+str(i))
            #来源
            elif TempStr == "bluray" or \
                 TempStr == "blu-ray" or \
                 TempStr == "hd-dvd" or \
                 TempStr == "uhd" or \
                 TempStr == "3d" or\
                 TempStr == "sbs" or\
                 TempStr == "h-sbs" or\
                 TempStr == "half-sbs" or\
                 TempStr == "nf" or\
                 TempStr == "itunes" or\
                 TempStr == "web-dl" or \
                 TempStr == "webrip" or \
                 TempStr == "hdtv" :
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                if self.source == "": self.source = FormatList[i]
                else:                 self.source += '-'+FormatList[i]
                movie_log ("find source:"+self.source+"i="+str(i))
            #压缩算法
            elif TempStr == "x265.10bit" or \
                 TempStr == "x265 10bit" or \
                 TempStr == "x265-10bit" :
                NumberOfElement += 2 ; LastIndex = i ; FormatSign[i] = 1
                self.compress = "x265" ; self.bit = "10bit"
                movie_log ("find compress and bit：x265.10bit")
            elif TempStr == "x264" or \
                 TempStr == "h264" or \
                 TempStr == "x265" or \
                 TempStr == "h265" or \
                 TempStr == "avc" or \
                 TempStr == "hevc" :
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.compress = FormatList[i]
                movie_log ("find compress:"+self.compress+"i="+str(i))
            #音频格式
            elif TempStr[0:3] == "dts" or \
                 TempStr[0:6] == "dts-hd" or \
                 TempStr[0:5] == "dtshd" or\
                 TempStr[0:3] == "ac3" or \
                 TempStr[0:3] == "aac" or \
                 TempStr[0:3] == "dd1" or \
                 TempStr[0:3] == "dd2" or \
                 TempStr[0:3] == "dd5" or \
                 TempStr[0:3] == "dda" or \
                 TempStr[0:3] == "ddp" or \
                 TempStr[0:3] == "dd+" or \
                 TempStr[0:4] == "lpcm" or \
                 TempStr[0:4] == "flac" or \
                 TempStr[0:4] == "opus" or \
                 TempStr[0:5] == "atmos" or \
                 TempStr[0:6] == "truehd" or \
                 TempStr[0:6] == "ddplus" or \
                 TempStr[0:7] == "true-hd" or \
                 TempStr == "dd" :     
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.audio += FormatList[i]
                movie_log ("find audio:"+self.audio+"i="+str(i))
                
                #音频格式比较复杂，后面可能还有信息被分割成下一个组了
                #所以，需要继续识别后面的组元素是否要加入音频格式
                
                while 1 == 1 and i+1 < len(FormatList) :
                    TempStr2 = (FormatList[i+1]).replace(' ','')   #去掉空格
                    TempStr2 = TempStr2.replace('.','')            #去掉'.'号
                    if TempStr2 == 'MA' or \
                       TempStr2 == 'MA5' or \
                       TempStr2 == 'MA51' or \
                       TempStr2 == 'MA7' or \
                       TempStr2 == 'MA71' or \
                       TempStr2 == 'MA20' or \
                       TempStr2 == '20' or \
                       TempStr2 == '51' or \
                       TempStr2 == '71' or \
                       TempStr2 == '0' or \
                       TempStr2 == '1' or \
                       TempStr2 == '2' or \
                       TempStr2 == '5' or \
                       TempStr2 == '6' or \
                       TempStr2 == '7' :
                        i += 1; LastIndex = i; FormatSign.append(1)
                        self.audio += FormatList[i]
                    else : #只要有一个不满足条件就跳出循环
                        break
                movie_log ("find audio-end："+self.audio)
            #音轨，如2audio
            elif TempStr[-5:] == "audio" or TempStr[-6:] == "audios":
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.track = FormatList[i]
                movie_log ("find track"+self.track+"i="+str(i))
            #色彩精度，10bit
            elif TempStr == "10bit" or TempStr == "8bit" :
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.bit = FormatList[i]
                movie_log ("find bit ："+self.bit+"i="+str(i))
            elif TempStr == "hdr" or\
                 TempStr == "hdr10" or\
                 TempStr == "hdrplus" or\
                 TempStr == "hdr10plus":
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                self.HDR = FormatList[i]
                movie_log ("find hdr"+"i="+str(i))
            elif TempStr == "mnhd" or\
                 TempStr == "muhd" :
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
                if self.zip_group == "" : self.zip_group = FormatList[i]
                else :                   self.zip_group = FormatList[i]+'-'+self.zip_group
                movie_log ("zip_group:"+self.zip_group+" i="+str(i))
            elif TempStr == "rev" :
                #忽略它
                NumberOfElement += 1 ; LastIndex = i ; FormatSign[i] = 1
            else:
                pass 
            
            if NumberOfElement == 1 and self.english_name == "": #第一次识别出关键字，那么之前的就是片名了        
                if i == 0: #第一个分割字符就是关键字，说明没有找到片名
                    ErrorLog("no name:"+self.dir_name)
                    self.IsError = 1; return 0
                j=0
                while j < i:
                    if j != 0 :
                        self.english_name += '.'
                    self.english_name += FormatList[j]
                    FormatSign[j] = 1
                    j += 1   
                movie_log ("name="+self.english_name)
            i += 1
            
        #end while i < len(FormatList)
        
        #识别出的最后关键字为压缩组
        i=LastIndex+1
        while i < len(FormatSign) :
            if self.zip_group == "": self.zip_group = FormatList[i]
            else :                 self.zip_group = FormatList[i]+'-'+self.zip_group
            FormatSign[i] = 1
            i += 1
        movie_log ("Group="+self.zip_group)
        
        #找出所有未识别的元素
        i = 0 ; Error = 0
        while i < len(FormatSign) :
            if FormatSign[i] == 0:
                movie_log ("unknown word:"+FormatList[i])
                Error = 1
            i += 1
            
        if Error == 1:
            return 0
        
        #重新组装 FormatStr
        String = ""
        if self.english_name != "" : String += self.english_name+"."
        if self.year != 0         : String += str(self.year)+"."
        if self.nation_version !="": String += self.nation_version+"."
        if self.version != ""     : String += self.version+"."
        if self.radio != ""       : String += self.radio+"."
        if self.special != ""     : String += self.special+"."
        if self.source != ""      : String += self.source +"."
        if self.compress != ""    : String += self.compress+"."
        if self.bit != ""         : String += self.bit+"."
        if self.HDR !=  ""        : String += self.HDR+"."
        if self.audio != ""       : String += self.audio+"."
        if self.track != ""       : String += self.track+"."
        if self.zip_group != ""    : String += self.zip_group
        movie_log("new format:"+String)
        #self.format_str = String
        return 1
    #end def split_format()
    
    def check_table(self):
        """
        进行插入表或者更新
        返回值：
            TABLE_ERROR  错误
        """
        if self.collection == 1:
            for i in range(len(self.sub_movie)):
                if self.check_table(self.sub_movie[i]) != SUCCESS: return TABLE_ERROR
            return SUCCESS
            
        if self.number <= 0 or self.copy < 0 : ErrorLog("number error:"+str(self.number)+"::"+str(self.copy)); return TABLE_ERROR

        dbMovie = Movie.from_db(number=self.number, copy=self.copy, total_size=self.total_size)
        if dbMovie is None:  #数据库中不存在插入
            if self.insert():
                ExecLog("insert movies:"+self.dir_name)
                return SUCCESS
            else:
                ExecLog("failed to insert movies:"+self.dir_name)
                return TABLE_ERROR
        #已经存在就update
        else:
            if self.compare_movie(dbMovie):   #和数据库比较,有变化
                if self.update(): 
                    ExecLog("update movies:"+self.dir_name)
                    return SUCCESS
                else:
                    ErrorLog("update error:"+self.dir_name)
                    return TABLE_ERROR
            else : 
                update("update movies set checked=1 where number=%s and copy=%s",(self.number,self.copy))
                movie_log("no change:"+self.dir_name)
                return SUCCESS

    def select(self,assign_value=True):
        if self.collection == 1 or self.number <= 0: return False

        se_sql = "select " \
            + "nation,type,name,Min,DirName,Radio,Version,NationVersion,special,source,compress,audio,track,bit,HDR,ZipGroup,Deleted,disk,IMDBID,DoubanID,size " \
            + "from movies where number=%s and copy=%s and size=%s"
        se_val = (self.number, self.copy, self.total_size)
        tSelectResult = select(se_sql,se_val)
        if tSelectResult == None or len(tSelectResult) == 0: return False
        tSelect = tSelectResult[0]
        if assign_value == True:
            self.nation        = tSelect[0] 
            self.type          = tSelect[1] 
            self.name          = tSelect[2] 
            self.min           = tSelect[3] 
            self.dir_name      = tSelect[4] 
            self.radio         = tSelect[5]
            self.version       = tSelect[6]
            self.nation_version = tSelect[7]
            self.special       = tSelect[8]
            self.source        = tSelect[9]
            self.compress      = tSelect[10]
            self.audio         = tSelect[11] 
            self.track         = tSelect[12] 
            self.bit           = tSelect[13]
            self.HDR           = tSelect[14] 
            self.zip_group     = tSelect[15] 
            self.deleted       = tSelect[16] 
            self.disk          = tSelect[17] 
            self.imdb_id       = tSelect[18] 
            self.douban_id     = tSelect[19] 
            self.total_size    = tSelect[20]
        return True

    def insert(self):
        if self.collection == 1 or self.number <= 0 or self.name == "" or self.nation == "" : return False

        tCurrentTime = datetime.datetime.now()
        tCurrentDateTime = tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')
        in_sql = "INSERT INTO movies " \
                +   "(number,copy,nation,type,name,min,DirName,Radio,Version,NationVersion,special,source,compress,audio,track,bit,HDR,ZipGroup,Deleted,disk,UpdateTime,CheckTime,checked,IMDBID,DoubanID,size) " \
            + "VALUES(%s    ,%s  ,%s    ,%s   ,%s ,%s ,%s     ,%s   ,%s     ,%s           ,%s     ,%s    ,%s      ,%s   ,%s   ,%s ,%s ,%s      ,%s     ,%s  ,%s        ,%s       ,%s     ,%s    ,%s      ,%s)"
        in_val= (self.number,self.copy,self.nation,self.type,self.name,self.min,self.dir_name,self.radio,self.version,self.nation_version,self.special,self.source,self.compress,self.audio,self.track,self.bit,self.HDR,self.zip_group,self.deleted,self.disk,tCurrentDateTime,tCurrentDateTime,self.checked,self.imdb_id,self.douban_id,self.total_size)
        return insert(in_sql,in_val)

    def update(self):
        if self.collection == 1 or self.number <= 0 or self.name == "" or self.nation == "" : return False

        tCurrentTime = datetime.datetime.now()
        tCurrentDateTime = tCurrentTime.strftime('%Y-%m-%d %H:%M:%S')
        up_sql = ("UPDATE movies set "
                "nation=%s,"
                "type=%s,"
                "name=%s,"
                "Min=%s,"
                "DirName=%s,"
                "Radio=%s,"
                "Version=%s,"
                "NationVersion=%s,"
                "special=%s,"
                "source=%s,"
                "compress=%s,"
                "audio=%s,"
                "track=%s,"
                "bit=%s,"
                "HDR=%s,"
                "ZipGroup=%s,"
                "Deleted=%s,"
                "disk=%s,"
                "updatetime=%s,"
                "CheckTime=%s,"
                "checked=%s "
                "where number=%s and copy=%s and size=%s")
        up_val = (
                self.nation,
                self.type,
                self.name,
                self.min,
                self.dir_name,
                self.radio,
                self.version,
                self.nation_version,
                self.special,
                self.source,
                self.compress,
                self.audio,
                self.track,
                self.bit,
                self.HDR,
                self.zip_group,
                self.deleted,
                self.disk,
                tCurrentDateTime,
                tCurrentDateTime,
                self.checked,
                self.number, self.copy, self.total_size)
        if not update(up_sql,up_val): return False

        #id单独update，因为可能数据库id不为空，但是内存中为空的(例如手动checkmovie时)
        self.update_id()
        return True

    def update_id(self):
        if self.imdb_id != ""  : update("update movies set imdbid=%s where number=%s and copy=%s",(self.imdb_id,self.number,self.copy))
        if self.douban_id != "": update("update movies set doubanid=%s where number=%s and copy=%s",(self.douban_id,self.number,self.copy))

    def update_or_insert(self):
        if self.collection == 1 or self.number <= 0: return False

        if self.select(assign_value=False): return self.update()
        else            : return self.insert()

    def compare_movie(self,tMovie):
        IsDiff = False
        if self.nation        != tMovie.nation       : ExecLog("diff nation:{}|{}".format(self.nation,tMovie.nation)); IsDiff = True
        if self.type          != tMovie.type         : ExecLog("diff type:{}|{}".format(self.type,tMovie.type)); IsDiff = True
        if self.name          != tMovie.name         : ExecLog("diff name:{}|{}".format(self.name,tMovie.name)); IsDiff = True
        if self.min           != tMovie.min          : ExecLog("diff min:{}|{}".format(self.min,tMovie.min)); IsDiff = True
        if self.dir_name       != tMovie.dir_name      : ExecLog("diff dir_name:{}|{}".format(self.dir_name,tMovie.dir_name)); IsDiff = True
        if self.radio         != tMovie.radio        : ExecLog("diff radio:{}|{}".format(self.radio,tMovie.radio)); IsDiff = True
        if self.version       != tMovie.version      : ExecLog("diff version:{}|{}".format(self.version,tMovie.version)); IsDiff = True
        if self.nation_version != tMovie.nation_version: ExecLog("diff nation_version:{}|{}".format(self.nation_version,tMovie.nation_version)); IsDiff = True
        if self.special       != tMovie.special      : ExecLog("diff special:{}|{}".format(self.special,tMovie.special)); IsDiff = True
        if self.source        != tMovie.source       : ExecLog("diff source:{}|{}".format(self.source,tMovie.source)); IsDiff = True
        if self.compress      != tMovie.compress     : ExecLog("diff compress:{}|{}".format(self.compress,tMovie.compress)); IsDiff = True
        if self.audio         != tMovie.audio        : ExecLog("diff audio:{}|{}".format(self.audio,tMovie.audio)); IsDiff = True
        if self.track         != tMovie.track        : ExecLog("diff track:{}|{}".format(self.track,tMovie.track)); IsDiff = True
        if self.bit           != tMovie.bit          : ExecLog("diff bit:{}|{}".format(self.bit,tMovie.bit)); IsDiff = True
        if self.HDR           != tMovie.HDR          : ExecLog("diff HDR:{}|{}".format(self.HDR,tMovie.HDR)); IsDiff = True
        if self.zip_group      != tMovie.zip_group     : ExecLog("diff zip_group:{}|{}".format(self.zip_group,tMovie.zip_group)); IsDiff = True
        if self.disk          != tMovie.disk         : ExecLog("diff disk:{}|{}".format(self.disk,tMovie.disk)); IsDiff = True
        if self.deleted       != tMovie.deleted      : ExecLog("diff deleted:{}|{}".format(self.deleted,tMovie.deleted)); IsDiff = True
        if self.imdb_id != ""   and self.imdb_id   != tMovie.imdb_id   : ExecLog("diff imdb_id:{}|{}".format(self.imdb_id,tMovie.imdb_id)); IsDiff = True
        if self.douban_id != "" and self.douban_id != tMovie.douban_id : ExecLog("diff douban_id:{}|{}".format(self.douban_id,tMovie.douban_id)); IsDiff = True
        if self.total_size != 0 and self.total_size != tMovie.total_size: ExecLog("diff total_size:{}|{}".foat(self.totail_size,tMovie.total_size)); isDiff = True
        return IsDiff

    def get_torrent(self):
        tFullDirName = os.path.join(self.dir_path,self.dir_name) 
        
        #从目录下找torrent文件
        for tFile in os.listdir(tFullDirName):
            if tFile[-8:] == '.torrent':
                self.torrent_file = os.path.join(tFullDirName,tFile)
            if tFile[-6:] == 'resume':
                self.resume_file = os.path.join(tFullDirName,tFile)
        if self.torrent_file != "": return True
        
        #从目录下的download.txt找downloadlink
        tDownloadTxtFile = os.path.join(tFullDirName,'download.txt')
        if os.path.isfile(tDownloadTxtFile):
            try:
                line = open(tDownloadTxtFile).read()
            except:
                ErrorLog("failed to read download txt file:{}".format(tDownloadTxtFile))
                return False
            self.hash,self.download_link = line.split('|',1)
        if self.hash != "" and self.download_link != "": return True

        #从download表中找符合的记录
        #通过hash找或者number，copy找
        if self.hash != "":
            tReturn = select("select downloadlink from download where hash=%s",(self.hash,))
            if len(tReturn) == 1 and tReturn[0][0] != "":
                self.download_link = tReturn[0][0]
                return True
        else:
            tReturn = select("select downloadlink,dirname from download where number=%s and copy=%s",(self.number,self.copy))
            if len(tReturn) == 1 and self.dir_name == tReturn[0][1] and tReturn[0][0] != "":
                self.download_link = tReturn[0][0]
                return True

        if self.torrent_file != "": return True
        return False

    def get_id_from_table(self):
        if self.number <= 0: return False

        tSelect = select("select imdbid,doubanid from movies where number=%s and copy=%s",(self.number,self.copy))
        if tSelect == None or len(tSelect) != 1:
            return False
        self.imdb_id = tSelect[0][0]
        self.douban_id = tSelect[0][1]
        
        if self.imdb_id == "" and self.douban_id == "":
            return False
        return True

    def get_id_from_rss(self):
        if self.get_torrent(): return False
        if self.hash == "": return False
        tSelectResult = select("select doubanid,imdbid from rss where hash=%s",(self.hash,))
        if tSelectResult == None or len(tSelectResult) == 0:
            movie_log(f"can't find record from rss where hash={self.hash}")
            return False
        for tSelect in tSelectResult:
            if tSelect[0] == "" or tSelect[1] == "": continue
            self.douban_id = tSelect[0]
            self.imdb_id = tSelect[1]
            movie_log(f"find id from rss:{self.douban_id}|{self.imdb_id}")
            return True
        return False

def MoveDirFile(SrcDir,DestDir) :
    """
    将SrcDir所有文件移到DestDir目录中
    返回值：
    SRC_NOT_DIR
    DEST_NOT_DIR
    DEPTH_ERROR
    UNKNOWN_FILE_TYPE
    FAILED_MOVE
    FAILED_RMDIR
    """
    if not os.path.isdir(SrcDir) :  return SRC_NOT_DIR
    if not os.path.isdir(DestDir) : return DEST_NOT_DIR
    
    NumberOfFile = 0
    FileName = []
    for file in os.listdir(SrcDir):
        FullPathFile = os.path.join(SrcDir,file)
        if os.path.isdir(FullPathFile): return DEPTH_ERROR
        elif os.path.isfile(FullPathFile):
            NumberOfFile += 1
            FileName.append(FullPathFile)
        else: return UNKNOWN_FILE_TYPE
    
    #逐个移动文件到目标文件夹
    for i in range(NumberOfFile):
        try:
            shutil.move(FileName[i],DestDir)
        except: 
            return FAILED_MOVE
    
    #删除这个空的srcDir
    try :
        os.rmdir(SrcDir)
    except:
        return FAILED_RMDIR

    return SUCCESS
#end def MoveDirFile

