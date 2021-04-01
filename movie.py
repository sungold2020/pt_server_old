#!/usr/bin/python3
# coding=utf-8
import shutil
from moviepy.editor import VideoFileClip
import torrentool.api

from database import *
from info import *

SUCCESS = 1
SRC_NOT_DIR = -1
DEST_NOT_DIR = -2
DEPTH_ERROR = -3
UNKNOWN_FILE_TYPE = -4
FAILED_MOVE = -5
FAILED_RMDIR = -6
TABLE_ERROR = -7

ENCODE = 0
BLUE_RAY = 1


class Movie:
    """
    一部电影存储在一个目录中，目录名带有电影的编号，名称，格式等信息
    """

    # 0表示测试，不执行修改，1表示执行修改
    tobe_exec_dir_name = True  # DirName名称
    tobe_exec_rmdir = False  # 从子文件夹将内容提上来 删除空子目录

    def __init__(self, dir_path="", dir_name="", disk=""):
        self.dir_name = dir_name  # 目录名称
        self.disk = disk  # 磁盘名 例如sg3t-2
        self.dir_path = dir_path  # 所在物理路径

        self.number = -1  # -1:error
        self.copy = 0  # 0 表示正本，其他表示不同版本1:3D版，2:加长版
        self.nation = ""  #
        self.type = MOVIE  # 0:Movie 1:TV 2:Record
        self.name = ""  #
        self.min = 0
        self.format_type = ENCODE  # 文件格式类型，0：重编码，1：蓝光原盘 

        # 从格式中获取的信息
        self.radio = ""  # 分辨率
        self.version = ""  # 版本，例如CC，DC
        self.nation_version = ""  # 国家版本，如韩版，日版:JPN
        self.special = ""  # 特别说明，例如rerip
        self.source = ""  # 来源，如Blu-Ray，Web-DL
        self.compress = ""  # 压缩算法,如x264
        self.audio = ""  # 音频格式，如DTS
        self.track = ""  # 音轨，如2audio
        self.bit = ""  # 色彩精度，10bit,8bit
        self.HDR = ""  # HDR
        self.zip_group = ""  # 压缩组

        self._total_size = 0  # 电影文件大小，unit:M 取值:torrent.total_size / (1024*1024)
        self.deleted = 0
        self._douban_id = ""  #
        self._imdb_id = ""  #
        self.update_time = ""
        self.check_time = ""

        self.checked = 1  #

        self.english_name = ""  # 英文片名（也可能是其他语种）
        self.year = 0  # 年份

        # 目录内容组成部分
        self.jpg = 0  # 是否有海报图片
        self.nfo = 0  # 是否有nfo文件
        self.number_of_SP = 0  # 花絮等的数量
        self.number_of_video = 0  # 不包含SP开头的视频文件，可能的几种情况
        # 0 :没有视频文件 
        # -1:有多个视频文件但不在定义的范围内 
        # >1:表示多个合集，可能发生的情况：
        #    1) 在纪录片和电视剧目录下，有效
        #    2) Part1/2,Disk1/2，任何两个文件名之间差别仅存在1个且为数字，有效
        #    3) 其他情况下，把它置为-1
        self.video_files = []  # 保存video文件名在数组中
        self.sample_video = ""  #

        self.hash = ""
        self.torrent_file = ""
        self.resume_file = ""
        self.download_link = ""
        self.IsError = 0  # 检查完以后是否有错误

        self.collection = 0  # 是否为合集
        self.number2 = 0  # 合集下的第二个数字
        self.sub_movie = []  # 合集下的对象
        self.sub_movie_count = 0  # 合集下的目录数量

        self.format_str = ""
        self.dir_name_todo = False  # 目录名称是否要修改

    @staticmethod
    def from_db(number=-1, copy=-1, total_size=0):
        db_movie = Movie()
        db_movie.number = number
        db_movie.copy = copy
        db_movie.total_size = total_size
        if db_movie.select():
            return db_movie
        return None

    @property
    def douban_id(self):
        return self._douban_id

    @douban_id.setter
    def douban_id(self, douban_id):
        self._douban_id = Info.check_douban_id(douban_id)

    @property
    def imdb_id(self):
        return self._imdb_id

    @imdb_id.setter
    def imdb_id(self, imdb_id):
        self._imdb_id = Info.check_imdb_id(imdb_id)

    @property
    def total_size(self):
        if self._total_size > 0:
            return self._total_size
        if not self.get_torrent():
            return 0
        try:
            torrent_info = torrentool.api.Torrent.from_file(self.torrent_file)
            self._total_size = int(torrent_info.total_size / (1024 * 1024))
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
        find_index = self.dir_name.find("-")
        if find_index == -1:
            Log.error_log("Error number:" + self.dir_name + "::")
            self.IsError = 1
            return False
        number_str = self.dir_name[0:find_index]
        lest = self.dir_name[find_index + 1:]
        if not (number_str.isdigit()):  # 不是数字的话。
            Log.error_log("invld Number1:" + self.dir_name + "::" + number_str)
            self.IsError = 1
            return False
        self.number = int(number_str)
        # 加入NumberStr小于4，则需要补零，至self.dir_name_todo = 1，留给Renamedir_name函数去补零
        if len(number_str) < 4:
            self.dir_name_todo = True

        # 继续找nation或者Copy或者Number2
        find_index = lest.find("-")
        if find_index == -1:
            Log.error_log("Error nation:" + self.dir_name + "::")
            self.IsError = 1
            return False
        self.nation = lest[0:find_index]
        lest = lest[find_index + 1:]
        # 如果nation是数字:
        # 1、是一个0-9的数字，则代表copy
        # 2、是长度>=4的数字字符，则说明是合集，先找出Number2，然后才是nation
        if self.nation.isdigit():
            if len(self.nation) == 1:  # copy
                self.copy = int(self.nation)
            elif len(self.nation) >= 4:  # 合集
                self.number2 = int(self.nation)
                if self.number2 <= self.number:  # 合集的第二个数字应该大于第一个
                    Log.error_log("Error number2:" + self.dir_name + "::" + self.nation)
                    self.IsError = 1
                    return False
                self.collection = 1
            else:
                Log.error_log("4- number2:" + self.dir_name + "::" + self.nation)
                self.IsError = 1
                return False

            # 继续找nation
            find_index = lest.find("-")
            if find_index == -1:
                Log.error_log("Error nation in collection:" + self.dir_name + "::" + lest)
                self.IsError = 1
                return False
            self.nation = lest[0:find_index]
            lest = lest[find_index + 1:]

        # 判断nation长度
        if len(self.nation) > 5:
            Log.error_log("5+length nation:" + self.dir_name + "::" + lest)
            self.IsError = 1
            return False

        # 如果前三个字符是电视剧或者纪录片
        if lest[0:3] == "纪录片":
            self.type = RECORD
        elif lest[0:3] == "电视剧":
            self.type = TV
        else:
            self.type = MOVIE
        if self.type != MOVIE:  # 电视剧或者纪录片
            if lest[3:4] != "-":
                Log.error_log("Error：not - :" + self.dir_name)
                self.IsError = 1
                return False
            lest = lest[4:]

        # 继续找name
        find_index = lest.find(" ")
        if find_index == -1:  # 说明name后面就空了，没有min和Format
            self.name = lest
            return True
        self.name = lest[0:find_index]
        lest = lest[find_index + 1:]

        # 继续找min
        find_index = lest.find("Min")
        if find_index == -1:
            # Log.movie_log ("No Min:"+self.dir_name)
            self.format_str = lest
            return True
        else:
            # Min后面没有了format
            if len(lest) == find_index + 3:
                self.min = int(lest[0:find_index].lstrip())
                # Log.movie_log("no format after Min:"+self.dir_name+"::"+str(self.min))
                return True
            # Min后的第一个字符是不是空格，如果不是表示Min可能是格式中的字符，例如Mind
            elif lest[find_index + 3:find_index + 4] != ' ':
                # Log.movie_log ("Min之后不是空格:"+Lest[FindIndex+3:FindIndex+4]+"::"+self.dir_name)
                self.format_str = lest
            else:
                min_str = lest[0:find_index].lstrip()  # Min之前的字符为MinStr,并去掉左边的空格符
                if not min_str.isdigit():
                    Log.error_log("Invalid Min:" + self.dir_name + "::" + min_str)
                    self.IsError = 1
                    return False
                self.min = int(min_str)
                self.format_str = lest[find_index + 4:]
        """
        if len(self.format_str) < 15:
            ErrorLog ("15- Format:"+self.dir_name+self.format_str)
            self.IsError = 1; return False
        """
        return True

    # end def check_dir_name

    def check_dir_cont(self):
        """ 
        :return: 
        """"""
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
        """

        if self.collection == 1:
            Log.error_log("Error:it is collection in CheckCont:" + self.dir_name)
            self.IsError = 1
            return False

        number_of_sub_dir = 0
        number_of_file = 0
        cover_jpg = 0
        post_jpg = 0
        sub_dir_name = ""  # 仅当NumberOfSubDir=1才有意义
        jpg_file_name = ""
        for file_name in os.listdir(os.path.join(self.dir_path, self.dir_name)):
            full_path_file = os.path.join(os.path.join(self.dir_path, self.dir_name), file_name)
            if os.path.isdir(full_path_file):
                if file_name[0:2] == "SP" or file_name[0:3] == "srt" \
                        or file_name[0:3] == "inf" or file_name[0:4] == "info":  # 忽略掉特殊文件夹
                    Log.movie_log("it is SP/srt/info DIR:" + file_name)
                    continue
                if os.path.islink(full_path_file):
                    Log.movie_log("it is a link:" + self.dir_name)
                    continue
                if file_name == "BDMV" or file_name == "CERTIFICATE":
                    self.format_type = BLUE_RAY
                    continue

                sub_dir_name = full_path_file
                number_of_sub_dir += 1
            elif os.path.isfile(full_path_file):
                number_of_file += 1
                # 视频文件
                if file_name[-3:] == "avi" or file_name[-3:] == "mkv" \
                        or file_name[-2:] == "ts" or file_name[-3:] == "mp4":
                    if file_name[0:2] == "SP":
                        Log.movie_log("find SP video:" + file_name)
                        self.number_of_SP += 1
                    elif re.search("sample", file_name, re.I):
                        Log.movie_log("find sample video:" + file_name + "::" + self.dir_name)
                        Log.error_log("sample video:" + file_name + "::" + self.dir_name)  # 仅记录，不做处理，待手工处理
                        self.sample_video = file_name
                    else:
                        self.number_of_video += 1
                        self.video_files.append(file_name)
                # jpg海报文件
                elif file_name[-3:] == "jpg" or file_name.endswith(".png"):
                    if file_name == "cover.jpg" or file_name == "cover.png":
                        cover_jpg = 1
                    elif file_name == "poster.jpg" or file_name == "poster.png":
                        post_jpg = 1
                    else:
                        jpg_file_name = file_name
                # nfo
                elif file_name[-3:].lower() == "nfo":
                    self.nfo = 1
                # torrent
                elif file_name[-6:] == 'resume' or file_name[-7:] == 'torrent' or file_name == 'download.txt':
                    pass
                elif file_name.endswith(".iso"):
                    self.format_type = BLUE_RAY
                elif file_name.endswith(".srt") \
                        or file_name.endswith(".ass") \
                        or file_name.endswith(".ssa") \
                        or file_name.endswith(".idx") \
                        or file_name.endswith(".sub"):
                    pass
                elif file_name.endswith(".txt"):
                    pass
                else:
                    Log.exec_log("other type file:" + file_name)
            else:
                Log.error_log("not file or dir :" + full_path_file)
                self.IsError = 1
                return False

        if number_of_sub_dir == 1:  # 除了srt/info/SP/之外有一个子目录
            if number_of_file == 0:  # 除了一个子目录外没有其他文件
                src_dir = os.path.join(os.path.join(self.dir_path, self.dir_name), sub_dir_name)
                dest_dir = os.path.join(self.dir_path, self.dir_name)
                if Movie.tobe_exec_rmdir:
                    if movie_dir_file(src_dir, dest_dir) == SUCCESS:
                        Log.exec_log("mv " + src_dir + " " + dest_dir)
                        return self.check_dir_cont()  # 已经移动文件夹成功，再重新检查
                    else:
                        Log.error_log("failed mv " + src_dir + " " + dest_dir)
                        self.IsError = 1
                        return False
                else:
                    Log.movie_log("todo mv " + src_dir + " " + dest_dir)
                    self.IsError = 1
                    return False
            else:  # 试图删除这个空的子目录，如果不成功，说明不是空的，报错
                try:
                    os.rmdir(sub_dir_name)
                    Log.exec_log("rmdir " + sub_dir_name)
                except Exception as err:
                    print(err)
                    Log.error_log("one not empty subdir:" + sub_dir_name)
                    self.IsError = 1
                    return False
        elif number_of_sub_dir > 1:
            Log.error_log("1+ subdir:" + self.dir_name)
            self.IsError = 1
            return False
        else:
            Log.movie_log("no subdir" + self.dir_name)

        # 检查海报
        current_path = os.path.join(self.dir_path, self.dir_name)
        if post_jpg == 1:
            if cover_jpg == 0:
                try:
                    src_file_name = os.path.join(current_path, "poster.jpg")
                    dest_file_name = os.path.join(current_path, "cover.jpg")
                    shutil.copyfile(src_file_name, dest_file_name)
                    Log.exec_log("cp poster.jpg cover.jpg in" + self.dir_name)
                    self.jpg = 1
                except Exception as err:
                    print(err)
                    Log.error_log("failed cp poster.jpg in" + self.dir_name)
                    self.IsError = 1
                    return False
            else:
                self.jpg = 1
        elif cover_jpg == 1:  # 没有poster.jpg但是有cover.jpg
            src_file_name = dest_file_name = ""
            try:
                src_file_name = os.path.join(current_path, "cover.jpg")
                dest_file_name = os.path.join(current_path, "poster.jpg")
                shutil.copyfile(src_file_name, dest_file_name)
                Log.exec_log("cp cover.jpg in" + self.dir_name)
                self.jpg = 1
            except Exception as err:
                print(err)
                Log.error_log("failed cp cover.jpg in" + self.dir_name)
                Log.movie_log("failed cp cover.jpg in" + self.dir_name)
                Log.movie_log(src_file_name)
                Log.movie_log(dest_file_name)
                self.IsError = 1
                return False
        elif jpg_file_name != "":  # 但是还有其他jpg文件
            try:
                src_file_name = os.path.join(current_path, jpg_file_name)
                dest_file_name = os.path.join(current_path, "poster.jpg")
                Log.movie_log("To CP:" + src_file_name)
                Log.movie_log("      " + dest_file_name)
                shutil.copyfile(src_file_name, dest_file_name)
                Log.exec_log("cp " + jpg_file_name + " poster.jpg in" + self.dir_name)
                dest_file_name = os.path.join(current_path, "cover.jpg")
                shutil.copyfile(src_file_name, dest_file_name)
                Log.movie_log("      " + dest_file_name)
                Log.exec_log("cp " + jpg_file_name + " cover.jpg in" + self.dir_name)
                self.jpg = 1
            except Exception as err:
                print(err)
                Log.error_log("failed cp " + jpg_file_name + " in" + self.dir_name)
                self.IsError = 1
                return False
        else:
            Log.error_log("no jpg file:" + self.dir_name)
            self.jpg = 0  # 标记，但不返回，不影响后续检查操作
        # print("check jpg complete")

        # 检查视频文件
        if self.format_type == ENCODE:
            if self.number_of_video == 0:
                Log.error_log("no video in" + self.dir_name)
                self.IsError = 1
                return False
            elif self.number_of_video == 1:
                # print("check video complete")
                return True
            else:  # >=2忽略SP/sample外，还有多个视频文件，则需要进一步分析
                if self.type == RECORD or self.type == TV:  # 电视剧/纪录片
                    pass
                else:
                    # 比较多个video名的差别，
                    # 如果长度一致，仅有一个字符的差别，且这个字符是数字。则OK，否则报错
                    # 先以第一个VideoFileName为比较对象，后面逐个VideoFileName和它比较
                    length = len(self.video_files[0])
                    for i in range(self.number_of_video):
                        if len(self.video_files[i]) != length:
                            Log.error_log("diff len video:" + self.dir_name)
                            Log.movie_log("diff len video:" + self.dir_name)
                            Log.movie_log("  1:" + self.video_files[0])
                            Log.movie_log("  2:" + self.video_files[i])
                            # self.number_of_video = -1
                            # self.IsError = 1 ; return False
        return True

    # end def check_dir_cont

    def get_runtime(self):
        """
        获取video的时长，多个video就累加。
        前置条件：执行过check_dir_cont，已经获取了self.video_files
        """
        if self.number_of_video <= 0:
            Log.movie_log("no video file:" + self.dir_name)
            return 0
        if self.type != MOVIE:
            return 0

        t_min = 0
        for i in range(self.number_of_video):
            full_path = os.path.join(self.dir_path, self.dir_name)
            movie_file = os.path.join(full_path, self.video_files[i])
            try:
                clip = VideoFileClip(movie_file)
                t_min += int(clip.duration / 60)
                clip.reader.close()
                clip.audio.reader.close_proc()
            except Exception as err:
                print(err)
                Log.exec_log("error:get runtime:" + self.dir_name)
                return 0
        return t_min

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
            #Log.movie_log ("not 1 video:"+self.dir_name)
            return 0
        if self.type != MOVIE:
            return 0

        tMin = 0
        for i in range(self.number_of_video):
            if (self.video_files[i])[-3:] != "mkv" :
                #Log.movie_log ("not mkvfile:"+self.dir_name)
                return 0

            Path = os.path.join(self.dir_path,self.dir_name)
            MkvName = os.path.join(Path,self.video_files[i])
            RunTimeStr='mkvinfo --ui-language en_US "'+MkvName+'" | grep Duration'
            Log.movie_log(RunTimeStr)
            #Log.movie_log (RunTimeStr)
            Line = os.popen(RunTimeStr).read()
            #Log.movie_log (Line[:24])
            Hour=Line[14:16]
            Min=Line[17:19]
            #Log.movie_log (Hour+" "+Min)
            if not ( Hour.isdigit() and Min.isdigit() ):
                #Log.movie_log ("Hour or Min isn't digit"+Hour+":"+Min)
                return 0

            MinNumber = int(Hour)*60 + int(Min)
            #Log.movie_log ("Min="+str(MinNumber))
            tMin += MinNumber
        return tMin
    '''

    def format_from_video_file(self):
        """
        从video_file中提取format，赋值到self.format_str
        前置条件：
        1、已经执行过check_dir_cont
        2、有且只有一个有效的视频文件NumberOfVideo == 1
        
        成功返回True，否则返回False
        """

        if not self.number_of_video == 1:
            Log.movie_log("2+Video,don't know how to find format from video")
            return False

        file_name = self.video_files[0]
        length = len(file_name)
        if file_name[-3:] == "mkv" or file_name[-3:] == "avi" or file_name[-3:] == "mp4":
            self.format_str = file_name[:length - 4]
            return 1
        elif file_name[-2:] == "ts":
            self.format_str = file_name[:length - 3]
            return True
        else:
            return False

    # end def format_from_video_file

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

        # Log.movie_log("begin rename_dir_name")
        if self.collection == 1:
            Log.error_log("Error:it is collection in rename_dir_name:" + self.dir_name)
            self.IsError = 1
            return False
        if self.number <= 0 or self.number >= 10000:
            Log.error_log("ErrorNumber:" + self.dir_name + "::" + str(self.number))
            self.IsError = 1
            return False
        if len(self.nation) == 0 or len(self.nation) >= 8:
            Log.error_log("8+nation :" + self.dir_name + "::" + self.nation)
            self.IsError = 1
            return False
        if len(self.name) == 0 or len(self.name) >= 20:
            Log.error_log("20+name :" + self.dir_name + "::" + self.name)
            self.IsError = 1
            return False

        # Log.movie_log (str(self.min))
        min_from_mkv = self.get_runtime()
        # Log.movie_log (str(min_from_mkv))
        if self.min == 0 and self.type == MOVIE:
            if min_from_mkv == 0:
                Log.error_log("not Found Min:" + self.dir_name)
                self.IsError = 1
                return False
            else:
                self.min = min_from_mkv
                self.dir_name_todo = True
        if self.type == MOVIE and min_from_mkv != 0 and abs(self.min - min_from_mkv) >= 2:
            Log.movie_log("Min-min_from_mkv >= 2:{}|{}".format(self.min, min_from_mkv))
            self.min = min_from_mkv
            self.dir_name_todo = True

        self.format_str = self.format_str.strip()  # 去掉前后空格
        Log.movie_log("Current formatstr;" + self.format_str)
        if len(self.format_str) == 0:
            # 从video 文件名里提取出格式文件
            if not self.format_from_video_file():
                Log.error_log("not found Format:" + self.dir_name)
                self.IsError = 1
                return False
            Log.movie_log("find Format:" + self.format_str)
            self.dir_name_todo = True
        elif len(self.format_str) <= 10:
            Log.error_log("10-Format:" + self.dir_name + "::" + self.format_str)
            self.IsError = 1
            return False
        else:
            Log.movie_log("correct format" + self.format_str)

        # 如果TODO=0，说明dir_name不需要修改
        if not self.dir_name_todo:
            Log.movie_log("Correct dir_name:" + self.dir_name)
            return True

        source_dir = os.path.join(self.dir_path, self.dir_name)
        number_str = (str(self.number)).zfill(4)
        if self.copy > 0:
            number_str = number_str + "-" + str(self.copy)

        if self.type == MOVIE:
            dest_dir_name = number_str + "-" + self.nation + "-" + self.name + " " + str(
                self.min) + "Min " + self.format_str
        elif self.type == TV:
            dest_dir_name = number_str + "-" + self.nation + "-电视剧-" + self.name + " " + self.format_str
        elif self.type == RECORD:
            dest_dir_name = number_str + "-" + self.nation + "-纪录片-" + self.name + " " + self.format_str
        else:
            Log.error_log("Error type:" + self.dir_name + "::" + int(self.type))
            self.IsError = 1
            return False

        dest_dir = os.path.join(self.dir_path, dest_dir_name)

        Log.movie_log("begin rename dirname:")
        if Movie.tobe_exec_dir_name:
            try:
                os.rename(source_dir, dest_dir)
                Log.exec_log("mv " + self.dir_name)
                Log.exec_log("   " + dest_dir_name)
                Log.movie_log("rename success")
                self.dir_name = dest_dir_name
                return True
            except Exception as err:
                print(err)
                Log.error_log("mv failed:" + self.dir_name)
                Log.error_log("          " + dest_dir_name)
                Log.movie_log("Mv failed:" + source_dir)
                Log.movie_log("          " + dest_dir)
                self.IsError = 1
                return False
        else:
            Log.movie_log("ToDo mv " + self.dir_name)
            Log.movie_log("        " + dest_dir_name)
            return True

    # end def rename_dir_name

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
        # 1、获取id，从movies表中查询，或者获取hash，然后从rss中获取id
        if self.imdb_id == "" and self.douban_id == "":
            if not self.get_id_from_table():
                print(f"{self.number}")
                Log.movie_log("empty imdb_id and douban_id in:" + self.dir_name)
                if self.get_id_from_rss():
                    self.update_id()
                else:
                    return False

        # 2、检索info表获取必要信息，并比较
        t_info = Info(self.douban_id, self.imdb_id)
        # print(f"{self.douban_id}|{self.imdb_id}|{tInfo.movie_name}|{tInfo.director}|{tInfo.actors}|{tInfo.nation}")
        if t_info.douban_status == OK:
            # 比较影片名是否一致
            if not (t_info.movie_name in self.name
                    or self.name in t_info.movie_name
                    or self.name in t_info.other_names):
                Log.error_log(f"name is diff:{self.name}|{t_info.movie_name}")
                # return False
            return True

        # print(tInfo.douban_status)
        print(f"douban_status={t_info.douban_status},re-spider douban:{self.number}")
        # 3、重新爬取影片信息，
        t_info.douban_status = RETRY
        if t_info.spider_douban() != OK:
            Log.exec_log("failed to spider_douban:" + self.dir_name)
            return False

        # 4、下载poster及更新info表
        t_current_path = os.path.join(self.dir_path, self.dir_name)
        if not os.path.isfile(os.path.join(t_current_path, 'poster.jpg')):
            t_info.download_poster(t_current_path)
        return t_info.update_or_insert()

    def check_movie(self):
        """
        用于checkmovie.py调用，完整检查目录。内容，等信息
        """

        # 1、检查dirname，获取number,copy,name,nation,min,format等
        if not self.check_dir_name():
            Log.error_log("failed check_dir_name:" + self.dir_name)
            self.IsError = 1
            return False

        # 从dirname获取是否collection
        if self.collection == 1:
            Log.movie_log("Begin collection" + self.dir_name)
            sub_dir_path = os.path.join(self.dir_path, self.dir_name)
            for file in os.listdir(sub_dir_path):
                full_path_file = os.path.join(sub_dir_path, file)
                if os.path.isdir(full_path_file):
                    self.sub_movie.append(Movie(sub_dir_path, file, self.disk))
                    if not self.sub_movie[-1].check_movie():
                        Log.error_log(f"check error:{full_path_file}")
                        return False
                    self.sub_movie_count += 1
            Log.movie_log("End collection" + self.dir_name)
            if self.sub_movie_count > 0:
                return True
            else:
                Log.error_log("empty collection:" + self.dir_name)
                self.IsError = 1
                return False
        # end if self.collection == 1

        # 2、检查format中的格式信息
        if self.split_format() == 0:
            Log.error_log("split_format:" + self.dir_name)
            self.IsError = 1
            # return 0  只记录错误，不返回

        # 3、检查id和info信息
        if not self.check_info():
            Log.error_log("failed check_info:" + self.dir_name)
            self.IsError = 1
            # return False

        # 4、检查dir中内容
        if not self.check_dir_cont():
            Log.error_log("failed check_dir_cont:" + self.dir_name)
            self.IsError = 1
            # return False

        # 5、如果dirname中,min，format格式不全，补充完整后更新dirname
        if not self.rename_dir_name():
            Log.error_log("failed rename_dir_name:" + self.dir_name)
            self.IsError = 1
            return False

        # 6、更新movie表信息
        if self.check_table() != SUCCESS:
            Log.error_log("check_table:" + self.dir_name)
            self.IsError = 1
            return False
        return True

    # end def check_movie

    def save_movie(self):
        """
        用于ptserver进行保存电影的入口，非必要性错误仅提示
        """

        if not self.check_dir_name():
            Log.error_log("failed check_dir_name:" + self.dir_name)
            self.IsError = 1
            return False

        if self.split_format() == 0:
            Log.error_log("split_format:" + self.dir_name)
            self.IsError = 1

        if not self.check_dir_cont():
            Log.error_log("failed check_dir_cont:" + self.dir_name)
            self.IsError = 1

        if not self.rename_dir_name():
            Log.error_log("failed rename_dir_name:" + self.dir_name)
            self.IsError = 1

        if self.check_table() != SUCCESS:
            Log.error_log("check_table:" + self.dir_name)
            self.IsError = 1
            return 0
        return 1

    # end def check_movie

    def split_format(self):
        """
        对Format进行分析，提取年份，分辨率，压缩算法等
        前置条件：
        check_dir_name必须已经执行，FormatStr已经获取
        """

        self.format_str = self.format_str.strip()
        if len(self.format_str) == 0:
            Log.error_log("no format:" + self.dir_name)
            self.IsError = 1
            return 0

        # 尝试进行空格分割
        # SplitSign = ' '
        format_list = self.format_str.split()
        if len(format_list) < 3:
            # 再尝试进行'.'分割
            format_list = self.format_str.split('.')
            if len(format_list) < 3:
                Log.error_log("3- format:" + self.format_str)
                self.IsError = 1
                return 0
            # else :
            # SplitSign = '.'

        # 处理最后一个group，通常是XXX-Group格式
        t_str = format_list[-1]
        t_index = t_str.rfind('-')
        if t_index > 0:
            format_list[-1] = t_str[:t_index]
            self.zip_group = t_str[t_index + 1:]

        number_of_element = 0  # 找到了几个关键字
        last_index = -1  # 找到关键字后要标记出它在FormatList中的索引
        format_sign = []  # 对应FormatList[]的标志位，0表示未识别，1表示已识别
        # beginfrom 1,0 must be englishname
        i = 1
        format_sign.append(0)
        while i < len(format_list):
            Log.movie_log("FormatList:i=" + str(i) + "::" + format_list[i])
            temp_str = format_list[i].lower()
            temp_str = temp_str.replace(' ', '')  # 删除空格并把它全部转换为小写，便于比较
            format_sign.append(0)

            # 年份：
            if temp_str.isdigit() and 1900 < int(temp_str) <= int(datetime.datetime.now().year):
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.year = int(format_list[i])
                Log.movie_log("find Year:" + str(self.year) + "i=" + str(i))
            # 版本
            elif temp_str == "cc" or \
                    temp_str == "dc" or \
                    temp_str == "extended" or \
                    temp_str == "open-matte" or \
                    temp_str == "the-final-cut" or \
                    temp_str == "uncut" or \
                    temp_str == "unrated" or \
                    temp_str == "complete" or \
                    temp_str == "re-grade" or \
                    temp_str == "cut":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                if self.version == "":
                    self.version = format_list[i]
                else:
                    self.version += '-' + format_list[i]
                Log.movie_log("find Version:" + self.version + "i=" + str(i))
            # 国家版本
            elif temp_str.upper() == "JPN" or \
                    temp_str.upper() == "GBR" or \
                    temp_str.upper() == "GER" or \
                    temp_str.upper() == "KOR" or \
                    temp_str.upper() == "ESP" or \
                    temp_str.upper() == "USA" or \
                    temp_str.upper() == "NLD" or \
                    temp_str.upper() == "FRA" or \
                    temp_str.upper() == "TW" or \
                    temp_str.upper() == "BFI" or \
                    temp_str.upper() == "TOHO" or \
                    temp_str.upper() == "US" or \
                    temp_str.upper() == "HK":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.nation_version = format_list[i]
                Log.movie_log("find nation_version:" + self.nation_version + "i=" + str(i))
            # 特别说明，例如rerip
            elif temp_str == "rerip" or \
                    temp_str == "remastered" or \
                    temp_str == "repack":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.special = format_list[i]
                Log.movie_log("find special:" + self.special + "i=" + str(i))
            # 分辨率
            elif temp_str == "720p" or \
                    temp_str == "1080p" or \
                    temp_str == "2160p" or \
                    temp_str == "1080i" or \
                    temp_str.lower() == "4k" or \
                    temp_str.lower() == "60fps" or \
                    re.match("[0-9][0-9][0-9][0-9]p", temp_str) is not None or \
                    re.match("[0-9][0-9][0-9][0-9]x[0-9][0-9][0-9]p", temp_str) is not None or \
                    re.match("[0-9][0-9][0-9][0-9]x[0-9][0-9][0-9][0-9]p", temp_str) is not None:
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                if self.radio == "":
                    self.radio = format_list[i]
                else:
                    self.radio += '.' + format_list[i]
                Log.movie_log("find Radio:" + self.radio + "i=" + str(i))
            # ignore 2d
            elif temp_str == "2d":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                Log.movie_log("ignore 2d:" + "i=" + str(i))
            # 来源
            elif temp_str == "bluray" or \
                    temp_str == "blu-ray" or \
                    temp_str == "hd-dvd" or \
                    temp_str == "uhd" or \
                    temp_str == "3d" or \
                    temp_str == "sbs" or \
                    temp_str == "h-sbs" or \
                    temp_str == "half-sbs" or \
                    temp_str == "nf" or \
                    temp_str == "itunes" or \
                    temp_str == "web-dl" or \
                    temp_str == "webrip" or \
                    temp_str == "hddvd" or \
                    temp_str == "hdtv":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                if self.source == "":
                    self.source = format_list[i]
                else:
                    self.source += '-' + format_list[i]
                Log.movie_log("find source:" + self.source + "i=" + str(i))
            # 压缩算法
            elif temp_str == "x265.10bit" or \
                    temp_str == "x265 10bit" or \
                    temp_str == "x265-10bit":
                number_of_element += 2
                last_index = i
                format_sign[i] = 1
                self.compress = "x265"
                self.bit = "10bit"
                Log.movie_log("find compress and bit：x265.10bit")
            elif temp_str == "x264" or \
                    temp_str == "h264" or \
                    temp_str == "x265" or \
                    temp_str == "h265" or \
                    temp_str == "avc" or \
                    temp_str == "hevc":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.compress = format_list[i]
                Log.movie_log("find compress:" + self.compress + "i=" + str(i))
            # 音频格式
            elif temp_str[0:3] == "dts" or \
                    temp_str[0:6] == "dts-hd" or \
                    temp_str[0:5] == "dtshd" or \
                    temp_str[0:3] == "ac3" or \
                    temp_str[0:3] == "aac" or \
                    temp_str[0:3] == "dd1" or \
                    temp_str[0:3] == "dd2" or \
                    temp_str[0:3] == "dd5" or \
                    temp_str[0:3] == "dda" or \
                    temp_str[0:3] == "ddp" or \
                    temp_str[0:3] == "dd+" or \
                    temp_str[0:4] == "lpcm" or \
                    temp_str[0:4] == "flac" or \
                    temp_str[0:4] == "opus" or \
                    temp_str[0:5] == "atmos" or \
                    temp_str[0:6] == "truehd" or \
                    temp_str[0:6] == "ddplus" or \
                    temp_str[0:7] == "true-hd" or \
                    temp_str == "dd":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.audio += format_list[i]
                Log.movie_log("find audio:" + self.audio + "i=" + str(i))

                # 音频格式比较复杂，后面可能还有信息被分割成下一个组了
                # 所以，需要继续识别后面的组元素是否要加入音频格式

                while 1 == 1 and i + 1 < len(format_list):
                    temp_str2 = (format_list[i + 1]).replace(' ', '')  # 去掉空格
                    temp_str2 = temp_str2.replace('.', '')  # 去掉'.'号
                    if temp_str2 == 'MA' or \
                            temp_str2 == 'MA5' or \
                            temp_str2 == 'MA51' or \
                            temp_str2 == 'MA7' or \
                            temp_str2 == 'MA71' or \
                            temp_str2 == 'MA20' or \
                            temp_str2 == '20' or \
                            temp_str2 == '51' or \
                            temp_str2 == '71' or \
                            temp_str2 == '0' or \
                            temp_str2 == '1' or \
                            temp_str2 == '2' or \
                            temp_str2 == '5' or \
                            temp_str2 == '6' or \
                            temp_str2 == '7':
                        i += 1
                        last_index = i
                        format_sign.append(1)
                        self.audio += format_list[i]
                    else:  # 只要有一个不满足条件就跳出循环
                        break
                Log.movie_log("find audio-end：" + self.audio)
            # 音轨，如2audio
            elif temp_str[-5:] == "audio" or temp_str[-6:] == "audios":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.track = format_list[i]
                Log.movie_log("find track" + self.track + "i=" + str(i))
            # 色彩精度，10bit
            elif temp_str == "10bit" \
                    or temp_str == "10bits" \
                    or temp_str == "8bit":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.bit = format_list[i]
                Log.movie_log("find bit ：" + self.bit + "i=" + str(i))
            elif temp_str == "hdr" or \
                    temp_str == "hdr10" or \
                    temp_str == "hdrplus" or \
                    temp_str == "hdr10plus":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                self.HDR = format_list[i]
                Log.movie_log("find hdr" + "i=" + str(i))
            elif temp_str == "mnhd" or \
                    temp_str == "muhd":
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
                if self.zip_group == "":
                    self.zip_group = format_list[i]
                else:
                    self.zip_group = format_list[i] + '-' + self.zip_group
                Log.movie_log("zip_group:" + self.zip_group + " i=" + str(i))
            elif temp_str == "rev" or re.match("s0[0-9]", temp_str):
                # 忽略它
                number_of_element += 1
                last_index = i
                format_sign[i] = 1
            else:
                pass

            if number_of_element == 1 and self.english_name == "":  # 第一次识别出关键字，那么之前的就是片名了
                if i == 0:  # 第一个分割字符就是关键字，说明没有找到片名
                    Log.error_log("no name:" + self.dir_name)
                    self.IsError = 1
                    return 0
                j = 0
                while j < i:
                    if j != 0:
                        self.english_name += '.'
                    self.english_name += format_list[j]
                    format_sign[j] = 1
                    j += 1
                Log.movie_log("name=" + self.english_name)
            i += 1

        # end while i < len(FormatList)

        # 识别出的最后关键字为压缩组
        i = last_index + 1
        while i < len(format_sign):
            if self.zip_group == "":
                self.zip_group = format_list[i]
            else:
                self.zip_group = format_list[i] + '-' + self.zip_group
            format_sign[i] = 1
            i += 1
        Log.movie_log("Group=" + self.zip_group)

        # 找出所有未识别的元素
        i = 0
        error = 0
        while i < len(format_sign):
            if format_sign[i] == 0:
                Log.movie_log("unknown word:" + format_list[i])
                error = 1
            i += 1

        if error == 1:
            return 0

        # 重新组装 FormatStr
        string = ""
        if self.english_name != "":
            string += self.english_name + "."
        if self.year != 0:
            string += str(self.year) + "."
        if self.nation_version != "":
            string += self.nation_version + "."
        if self.version != "":
            string += self.version + "."
        if self.radio != "":
            string += self.radio + "."
        if self.special != "":
            string += self.special + "."
        if self.source != "":
            string += self.source + "."
        if self.compress != "":
            string += self.compress + "."
        if self.bit != "":
            string += self.bit + "."
        if self.HDR != "":
            string += self.HDR + "."
        if self.audio != "":
            string += self.audio + "."
        if self.track != "":
            string += self.track + "."
        if self.zip_group != "":
            string += self.zip_group
        Log.movie_log("new format:" + string)
        # self.format_str = string
        return 1

    # end def split_format()

    def check_table(self):
        """
        进行插入表或者更新
        返回值：
            TABLE_ERROR  错误
        """
        if self.collection == 1:
            for i in range(len(self.sub_movie)):
                if self.sub_movie[i].check_table() != SUCCESS:
                    return TABLE_ERROR
            return SUCCESS

        if self.number <= 0 or self.copy < 0:
            Log.error_log("number error:" + str(self.number) + "::" + str(self.copy))
            return TABLE_ERROR

        db_movie = Movie.from_db(number=self.number, copy=self.copy, total_size=self.total_size)
        if db_movie is None:  # 数据库中不存在插入
            if self.insert():
                Log.exec_log("insert movies:" + self.dir_name)
                return SUCCESS
            else:
                Log.exec_log("failed to insert movies:" + self.dir_name)
                return TABLE_ERROR
        # 已经存在就update
        else:
            if self.compare_movie(db_movie):  # 和数据库比较,有变化
                if self.update():
                    Log.exec_log("update movies:" + self.dir_name)
                    return SUCCESS
                else:
                    Log.error_log("update error:" + self.dir_name)
                    return TABLE_ERROR
            else:
                update("update movies set checked=1 where number=%s and copy=%s", (self.number, self.copy))
                Log.movie_log("no change:" + self.dir_name)
                return SUCCESS

    def select(self, assign_value=True):
        if self.collection == 1 or self.number <= 0:
            return False

        se_sql = "select nation,type,name,Min,DirName,Radio,Version,NationVersion,special,source,compress," \
                 "audio,track,bit,HDR,ZipGroup,Deleted,disk,IMDBID,DoubanID,size " \
                 "from movies where number=%s and copy=%s and size=%s"
        se_val = (self.number, self.copy, self.total_size)
        t_select_result = select(se_sql, se_val)
        if t_select_result is None or len(t_select_result) == 0:
            return False
        t_select = t_select_result[0]
        if assign_value:
            self.nation = t_select[0]
            self.type = t_select[1]
            self.name = t_select[2]
            self.min = t_select[3]
            self.dir_name = t_select[4]
            self.radio = t_select[5]
            self.version = t_select[6]
            self.nation_version = t_select[7]
            self.special = t_select[8]
            self.source = t_select[9]
            self.compress = t_select[10]
            self.audio = t_select[11]
            self.track = t_select[12]
            self.bit = t_select[13]
            self.HDR = t_select[14]
            self.zip_group = t_select[15]
            self.deleted = t_select[16]
            self.disk = t_select[17]
            self.imdb_id = t_select[18]
            self.douban_id = t_select[19]
            self.total_size = t_select[20]
        return True

    def insert(self):
        if self.collection == 1 or self.number <= 0 or self.name == "" or self.nation == "":
            return False

        t_current_time = datetime.datetime.now()
        t_current_date_time = t_current_time.strftime('%Y-%m-%d %H:%M:%S')
        in_sql = "INSERT INTO movies " \
                 "(number,copy,nation,type,name,min,DirName,Radio,Version,NationVersion,special,source,compress," \
                 "audio,track,bit,HDR,ZipGroup,Deleted,disk,UpdateTime,CheckTime,checked,IMDBID,DoubanID,size) " \
                 "VALUES(%s    ,%s  ,%s    ,%s   ,%s ,%s ,%s     ,%s   ,%s     ,%s           ,%s     ,%s    ,%s ," \
                 "%s   ,%s   ,%s ,%s ,%s      ,%s     ,%s  ,%s        ,%s       ,%s     ,%s    ,%s      ,%s)"
        in_val = (self.number, self.copy, self.nation, self.type, self.name, self.min, self.dir_name, self.radio,
                  self.version, self.nation_version, self.special, self.source, self.compress, self.audio, self.track,
                  self.bit, self.HDR, self.zip_group, self.deleted, self.disk, t_current_date_time, t_current_date_time,
                  self.checked, self.imdb_id, self.douban_id, self.total_size)
        return insert(in_sql, in_val)

    def update(self):
        if self.collection == 1 or self.number <= 0 or self.name == "" or self.nation == "":
            return False

        t_current_time = datetime.datetime.now()
        t_current_date_time = t_current_time.strftime('%Y-%m-%d %H:%M:%S')
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
            t_current_date_time,
            t_current_date_time,
            self.checked,
            self.number, self.copy, self.total_size)
        if not update(up_sql, up_val):
            return False

        # id单独update，因为可能数据库id不为空，但是内存中为空的(例如手动checkmovie时)
        self.update_id()
        return True

    def update_id(self):
        if self.imdb_id != "":
            update("update movies set imdbid=%s where number=%s and copy=%s", (self.imdb_id, self.number, self.copy))
        if self.douban_id != "":
            update("update movies set doubanid=%s where number=%s and copy=%s",
                   (self.douban_id, self.number, self.copy))

    def update_or_insert(self):
        if self.collection == 1 or self.number <= 0:
            return False

        if self.select(assign_value=False):
            return self.update()
        else:
            return self.insert()

    def compare_movie(self, t_movie):
        is_diff = False
        if self.nation != t_movie.nation:
            Log.exec_log("diff nation:{}|{}".format(self.nation, t_movie.nation))
            is_diff = True
        if self.type != t_movie.type:
            Log.exec_log("diff type:{}|{}".format(self.type, t_movie.type))
            is_diff = True
        if self.name != t_movie.name:
            Log.exec_log("diff name:{}|{}".format(self.name, t_movie.name))
            is_diff = True
        if self.min != t_movie.min:
            Log.exec_log("diff min:{}|{}".format(self.min, t_movie.min))
            is_diff = True
        if self.dir_name != t_movie.dir_name:
            Log.exec_log("diff dir_name:{}|{}".format(self.dir_name, t_movie.dir_name))
            is_diff = True
        if self.radio != t_movie.radio:
            Log.exec_log("diff radio:{}|{}".format(self.radio, t_movie.radio))
            is_diff = True
        if self.version != t_movie.version:
            Log.exec_log("diff version:{}|{}".format(self.version, t_movie.version))
            is_diff = True
        if self.nation_version != t_movie.nation_version:
            Log.exec_log("diff nation_version:{}|{}".format(self.nation_version, t_movie.nation_version))
            is_diff = True
        if self.special != t_movie.special:
            Log.exec_log("diff special:{}|{}".format(self.special, t_movie.special))
            is_diff = True
        if self.source != t_movie.source:
            Log.exec_log("diff source:{}|{}".format(self.source, t_movie.source))
            is_diff = True
        if self.compress != t_movie.compress:
            Log.exec_log("diff compress:{}|{}".format(self.compress, t_movie.compress))
            is_diff = True
        if self.audio != t_movie.audio:
            Log.exec_log("diff audio:{}|{}".format(self.audio, t_movie.audio))
            is_diff = True
        if self.track != t_movie.track:
            Log.exec_log("diff track:{}|{}".format(self.track, t_movie.track))
            is_diff = True
        if self.bit != t_movie.bit:
            Log.exec_log("diff bit:{}|{}".format(self.bit, t_movie.bit))
            is_diff = True
        if self.HDR != t_movie.HDR:
            Log.exec_log("diff HDR:{}|{}".format(self.HDR, t_movie.HDR))
            is_diff = True
        if self.zip_group != t_movie.zip_group:
            Log.exec_log("diff zip_group:{}|{}".format(self.zip_group, t_movie.zip_group))
            is_diff = True
        if self.disk != t_movie.disk:
            Log.exec_log("diff disk:{}|{}".format(self.disk, t_movie.disk))
            is_diff = True
        if self.deleted != t_movie.deleted:
            Log.exec_log("diff deleted:{}|{}".format(self.deleted, t_movie.deleted))
            is_diff = True
        if self.imdb_id != "" and self.imdb_id != t_movie.imdb_id:
            Log.exec_log("diff imdb_id:{}|{}".format(self.imdb_id, t_movie.imdb_id))
            is_diff = True
        if self.douban_id != "" and self.douban_id != t_movie.douban_id:
            Log.exec_log("diff douban_id:{}|{}".format(self.douban_id, t_movie.douban_id))
            is_diff = True
        if self.total_size != 0 and self.total_size != t_movie.total_size:
            Log.exec_log("diff total_size:{}|{}".format(self.total_size, t_movie.total_size))
            is_diff = True
        return is_diff

    def get_torrent(self):
        if self.dir_name == "" or self.dir_path == "":
            return False

        t_full_dir_name = os.path.join(self.dir_path, self.dir_name)

        # 从目录下找torrent文件
        for tFile in os.listdir(t_full_dir_name):
            if tFile[-8:] == '.torrent':
                self.torrent_file = os.path.join(t_full_dir_name, tFile)
            if tFile[-6:] == 'resume':
                self.resume_file = os.path.join(t_full_dir_name, tFile)
        if self.torrent_file != "":
            return True

        # 从目录下的download.txt找downloadlink
        t_download_txt_file = os.path.join(t_full_dir_name, 'download.txt')
        if os.path.isfile(t_download_txt_file):
            try:
                line = open(t_download_txt_file).read()
            except Exception as err:
                print(err)
                Log.error_log("failed to read download txt file:{}".format(t_download_txt_file))
                return False
            self.hash, self.download_link = line.split('|', 1)
        if self.hash != "" and self.download_link != "":
            return True

        # 从download表中找符合的记录
        # 通过hash找或者number，copy找
        if self.hash != "":
            t_return = select("select downloadlink from download where hash=%s", (self.hash,))
            if len(t_return) == 1 and t_return[0][0] != "":
                self.download_link = t_return[0][0]
                return True
        else:
            t_return = select("select downloadlink,dirname from download where number=%s and copy=%s",
                              (self.number, self.copy))
            if len(t_return) == 1 and self.dir_name == t_return[0][1] and t_return[0][0] != "":
                self.download_link = t_return[0][0]
                return True

        if self.torrent_file != "":
            return True
        return False

    def get_id_from_table(self):
        if self.number <= 0:
            return False

        t_select = select("select imdbid, doubanid from movies where number=%s", (self.number,))
        if t_select is None or len(t_select) == 0:
            return False
        self.imdb_id = t_select[0][0]
        self.douban_id = t_select[0][1]

        if self.imdb_id == "" and self.douban_id == "":
            return False
        return True

    def get_id_from_rss(self):
        if self.get_torrent():
            return False
        if self.hash == "":
            return False
        t_select_result = select("select doubanid,imdbid from rss where hash=%s", (self.hash,))
        if t_select_result is None or len(t_select_result) == 0:
            Log.movie_log(f"can't find record from rss where hash={self.hash}")
            return False
        for tSelect in t_select_result:
            if tSelect[0] == "" or tSelect[1] == "":
                continue
            self.douban_id = tSelect[0]
            self.imdb_id = tSelect[1]
            Log.movie_log(f"find id from rss:{self.douban_id}|{self.imdb_id}")
            return True
        return False


def movie_dir_file(src_dir, dest_dir):
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
    if not os.path.isdir(src_dir):
        return SRC_NOT_DIR
    if not os.path.isdir(dest_dir):
        return DEST_NOT_DIR

    number_of_file = 0
    file_name = []
    for file in os.listdir(src_dir):
        full_path_file = os.path.join(src_dir, file)
        if os.path.isdir(full_path_file):
            return DEPTH_ERROR
        elif os.path.isfile(full_path_file):
            number_of_file += 1
            file_name.append(full_path_file)
        else:
            return UNKNOWN_FILE_TYPE

    # 逐个移动文件到目标文件夹
    for i in range(number_of_file):
        try:
            shutil.move(file_name[i], dest_dir)
        except Exception as err:
            print(err)
            return FAILED_MOVE

    # 删除这个空的srcDir
    try:
        os.rmdir(src_dir)
    except Exception as err:
        print(err)
        return FAILED_RMDIR

    return SUCCESS
# end def MoveDirFile
