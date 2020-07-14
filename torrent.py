import datetime
import time
import os

class Torrent:
    def __init__(self,mClient="QB",mTorrent=None):
        self.client  = mClient
        self.torrent = mTorrent

        self.date_data = []
        #tCurrentTime = datetime.datetime.now()
        #tToday = tCurrentTime.strftime('%Y-%m-%d')
        #self.date_data.append({'date':tToday,'data':self.uploaded})

        #tFiles = []            #存储文件的数组,#名字,大小，完成率
        self.dir_name = ""             #种子目录名称
        self.root_folder = ""          #种子保存的路径所在根目录

        self.error_string = ""
        
    @property
    def hash(self):
        if self.torrent == None:  return ""
        if   self.client == "TR": return self.torrent.hashString
        elif self.client == "QB": return self.torrent.hash
        else:                   return ""
    @property
    def name(self):
        if self.torrent == None: return ""
        return self.torrent.name
    @property
    def progress(self):
        if self.torrent == None: return 0
        if   self.client == "TR": return int(self.torrent.percentDone*100)
        elif self.client == "QB": return int(self.torrent.progress*100)
        else:                   return 0
    @property
    def status(self):
        if self.torrent == None: return ""
        if   self.client == "TR": 
            if self.torrent.status[0:4].lower() == "stop": return "STOP"
            else                                         : return "GOING"
        elif self.client == "QB": 
            if self.torrent.state[0:5].lower() == "pause": return "STOP"
            else                                         : return "GOING"
        else:                   return "error"
    @property
    def category(self):
        if self.torrent == None: return ""
        if   self.client == "TR": return ""
        elif self.client == "QB": return self.torrent.category
        else                  : return ""
    @property
    def tags(self):
        if self.torrent == None: return ""
        if   self.client == "TR": return ""
        elif self.client == "QB": return self.torrent.tags
        else                  : return ""
    @property
    def save_path(self):
        if self.torrent == None: return ""
        if   self.client == "TR": return self.torrent.downloadDir
        elif self.client == "QB": return self.torrent.save_path
        else                  : return ""
    @property
    def add_datetime(self):
        if self.torrent == None: return ""
        if   self.client == "TR": return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.torrent.addedDate))
        elif self.client == "QB": return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.torrent.added_on))
        else                  : return ""
    @property
    def tracker(self):
        if self.torrent == None: return ""
        if   self.client == "TR": return self.torrent.trackers[0]['announce']
        elif self.client == "QB": return self.torrent.tracker
        else                  : return ""
    @property
    def uploaded(self):
        if self.torrent == None: return 0
        if   self.client == "TR": return self.torrent.uploadedEver
        elif self.client == "QB": return self.torrent.uploaded
        else                  : return 0
    @property
    def total_size(self):
        if self.torrent == None: return 0
        if   self.client == "TR": return self.torrent.totalSize
        elif self.client == "QB": return self.torrent.total_size
        else                  : return 0
    @property
    def files(self):
        if self.torrent == None: return []
        tFiles = []
        if   self.client == "TR": 
            tTorrentFiles = self.torrent.files()
            for i in range(len(tTorrentFiles)):
                tName = tTorrentFiles[i]['name']
                tSize = tTorrentFiles[i]['size']
                tProgress = int((tTorrentFiles[i]['completed']/tTorrentFiles[i]['size'])*100)
                tFiles.append({'name':tName,'size':tSize,'progress':tProgress})
        elif self.client == "QB": 
            tTorrentFiles = self.torrent.files
            for i in range(len(tTorrentFiles)):
                tName = tTorrentFiles[i].name
                tSize = tTorrentFiles[i].size
                tProgress = int(tTorrentFiles[i].progress*100)
                tFiles.append({'name':tName,'size':tSize,'progress':tProgress})
        else: pass
        return tFiles
    
    
    def stop(self):
        if self.torrent == None: self.error_string = "torrent does not exist"; return False
        if   self.client == "TR": 
            try: 
                self.torrent.stop()
            except Exception as err:
                print(err)
                return False
            else: 
                return True
        elif self.client == "QB": 
            try: 
                self.torrent.pause()
            except Exception as err:
                print(err)
                return False
            else: 
                return True
        else: return False

    def pause(self):
        if self.torrent == None: self.error_string = "torrent does not exist"; return False
        try:
            if self.client == "QB":
                self.torrent.pause()
            else:
                self.torrent.stop()
        except Exception as err:
            print(err)
            return False
        else:
            return True

    def resume(self):
        if self.torrent == None: self.error_string = "torrent does not exist"; return False
        try:
            if self.client == "QB":
                self.torrent.resume()
            else:
                self.torrent.start()
        except Exception as err:
            print(err)
            return False
        else:
            return True

    '''
    def start(self):
        if self.torrent == None: self.error_string = "torrent does not exist"; return False
        tBTStat =  os.statvfs(DOWNLOAD_FOLDER)
        tFreeSize = (tBTStat.f_bavail * tBTStat.f_frsize) /(1024*1024*1024)
        #DebugLog("free size:"+str(tFreeSize))
        tSize = self.total_size /(1024*1024*1024)
        #DebugLog("Size:"+str(tSize))
        if tFreeSize < tSize+1 :self.error_string = "diskspace is not enough"; return False
        if  self.resume() and self.set_category("下载"):
            return True
        else:
            self.error_string = ("failed to start torrent:"+self.name)
            return False
    '''

    def set_category(self,mCategory=""):
        if self.torrent == None: return False
        if   self.client == "TR": return False
        elif self.client == "QB": 
            try:
                self.torrent.set_category(mCategory)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else : return False

    def set_tags(self,mTags):
        if self.torrent == None: return False
        if   self.client == "TR": return False
        elif self.client == "QB": 
            try:
                self.torrent.remove_tags()
                self.torrent.add_tags(mTags)
            except Exception as err:
                print(err)
                return False
            else:
                return True
        else:
            return False

    def check_files(self,mIsNewDay):
        """
        检查文件是否存在及大小是否一致。
        mIsNewDay的话，完整检查。否则仅检查QB的类别为"下载"及"刷上传"的种子的第一个文件
        """
        if self.torrent == None: self.error_string = "torrent does not exist"; return False
        tFiles = self.files
        if mIsNewDay == True :
            for i in  range(len(tFiles)):
                if tFiles[i]['progress'] != 100: continue
                tFullFileName = os.path.join(self.save_path, tFiles[i]['name'])
                if not os.path.isfile(tFullFileName):
                    self.error_string = tFullFileName+" does not exist"
                    return False
                if tFiles[i]['size'] != os.path.getsize(tFullFileName) :
                    self.error_string = (tFullFileName+" file size error. torrent size:"+str(tFiles[i]['size']))
                    return False
        else: #不是新的一天，对于非转移/保种/低上传分类的种子，仅检查第一个下载完成的文件是否存在
            if self.client == "TR" : pass
            if self.category == "下载" or self.category == "刷上传" :
                #DebugLog("check torrent file:"+self.Name+"::"+self.save_path)
                for i in  range(len(tFiles)):
                    if tFiles[i]['progress'] != 100: continue
                    tFullFileName = os.path.join(self.save_path, tFiles[0]['name'])
                    if not os.path.isfile(tFullFileName) :
                        self.error_string = (tFullFileName+" does not exist")
                        return False
                    else: break
        return True
        
    def is_low_upload(self,mNumberOfDays,mUploadThreshold):
        #包括今天在内，至少要有NUMBEROFDAYS+1天数据
        tLength = len(self.date_data)
        if tLength < mNumberOfDays + 1:  return False

        #从尾部开始循环，尾部日期是最新的
        i = tLength - 1; tDays = 0  
        while i > 1 and tDays < mNumberOfDays:
            tDeltaData = (self.date_data[i])['data'] - (self.date_data[i-1])['data']
            if tDeltaData/self.total_size < mUploadThreshold :
                tDays += 1
            else:    
                return False  #有一天高于阈值就退出
            i -= 1
        
        return True
        
    def is_root_folder(self):
        tFiles = self.files

        #如何判断是否创建了子文件夹IsRootFolder，所有的文件都包含了目录，而且是一致的。
        tSubDirName = ""
        for i in range(len(tFiles)) :
            tIndex = (tFiles[i]['name']).find('/')
            if tIndex == -1 :  return False
            if tSubDirName == "":
                tSubDirName = (tFiles[i]['name'])[0:tIndex]
            else :
                if (tFiles[i]['name'])[0:tIndex] != tSubDirName : return False

        return True
