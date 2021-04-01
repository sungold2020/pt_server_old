#!/usr/bin/python3
# coding=utf-8
import psutil

import movie
from connect import *
from torrents import *
from sites import *


def handle_task(request):
    global gTorrents

    Log.socket_log("accept request:" + request)
    request_list = []
    dict_request = None
    # 尝试json解析
    try:
        dict_request = json.loads(request)
        task = dict_request['task']
    except json.JSONDecodeError:  # json解析失败，就按照以前方式解析
        request_list = request.split()
        if request_list is None or len(request_list) == 0:
            Log.exec_log(f"unknown request:{request}")
            return f"failed,unknown request {request}"
        task = request_list[0].lower()
        del request_list[0]
    except Exception as err:
        print(err)
        return f"failed:{str(err)}"

    if   task == 'checkdisk'    :
        if len(request_list) > 0 : gTorrents.check_disk(request_list)
        else                    : gTorrents.check_disk(SysConfig.CHECK_DISK_LIST)
    elif task == 'rss'          :
        for rss_name in request_list: gTorrents.request_torrents_from_rss_by_name(rss_name)
    elif task == 'free'     :
        if len(request_list) > 0 : gTorrents.request_torrents_from_page_by_name(request_list[0])
        else                    : gTorrents.request_torrents_from_page_by_name('MTeam')
    elif task == 'checkqb'      : gTorrents.check_torrents("QB")
    elif task == 'checktr'      : gTorrents.check_torrents("TR")
    elif task == 'keep'         : return keep_torrents(request_list)
    elif task == 'set_id'       : return gTorrents.request_set_id(request_list[0] if len(request_list) == 1 else "")
    elif task == 'set_category' : return gTorrents.request_set_category(request_list[0] if len(request_list) == 1 else "")
    elif task == 'view'         :
        if len(request_list) == 1 and request_list[0] == 'all': return str(update_viewed(False))
        else                                                : return str(update_viewed(True))
    elif task == 'lowupload'    : return gTorrents.print_low_upload()
    elif task == 'torrents'     : return gTorrents.query_torrents(request_list)
    elif task == "del"          : return gTorrents.request_del_torrent(request_list[0] if len(request_list) == 1 else "")
    elif task == "act_torrent"  : return gTorrents.request_act_torrent(request_list[0] if len(request_list) == 1 else "")
    elif task == "get_tracker_message" : return gTorrents.request_tracker_message(request_list[0] if len(request_list) == 1 else "")
    elif task == "set_info"     : return set_info(request_list[0] if len(request_list) == 1 else "")
    elif task == "get_info"     : return get_info(request_list[0] if len(request_list) == 1 else "")
    elif task == "set_remark"   : return set_remark(dict_request)
    elif task == "bookmark"     : return gTorrents.handle_bookmark(dict_request)
    elif task == 'log'          : return get_log()
    elif task == 'speed'        : return get_speed()
    elif task == 'freespace'    : return get_free_space()
    elif task == 'query_movies' : return query_movies(dict_request)
    elif task == 'del_movie'    : return del_movie(dict_request)
    elif task == 'query_dbmovie_detail' : return query_dbmovie_detail(dict_request)
    elif task == 'set_viewed'   : return set_viewed(dict_request)
    elif task == 'set_dbmovie_info': return set_dbmovie_info(dict_request)
    elif task == 'set_dbmovie_id': return set_dbmovie_id(dict_request)
    elif task == 'douban_cookie': return check_douban_cookie()
    elif task == 'load_sys_config': return SysConfig.load_sys_config()
    elif task == 'load_site_config': return SysConfig.load_site_config()
    else                        : Log.socket_log("unknown request task:"+task); return "unknown request task"
    
    return "completed"


def get_log():
    last_lines = mylib.get_last_lines(Log.EXEC_LOG_FILE, 300)
    return "\n".join(last_lines)


def get_speed():
    qb_client = PTClient("QB")
    tr_client = PTClient("TR")
    if not(qb_client.connect() and tr_client.connect()):
        return "速度:未知"
    return "QB: {:.1f}M/s↓ {:.2f}M/s↑\nTR: {:.1f}M/s↓ {:.2f}M/s↑".format(
                qb_client.down_speed/1024, qb_client.up_speed/1024,
                tr_client.down_speed/1024, tr_client.up_speed/1024)


def get_free_space():
    free_size = mylib.get_free_size(SysConfig.DOWNLOAD_FOLDER)
    return "{:.0f}".format(free_size)


def set_info(request_str):
    try:
        douban_id, imdb_id, movie_name, nation, director, actors, poster, genre, type_str = request_str.split('|', 8)
    except Exception as err:
        print(err)
        Log.exec_log("failed to split:" + request_str)
        return "failed:error requeststr:" + request_str
   
    info = Info(douban_id, imdb_id)
    info.movie_name = movie_name
    info.nation     = nation
    info.director   = director
    info.actors     = actors
    info.poster     = poster
    info.genre      = genre
    info.type       = int(type_str)
    info.douban_status = OK
    if info.update_or_insert():
        # efresh torrents info in memory
        gTorrents.set_info(douban_id, imdb_id)
        return "Success"
    return "更新info表失败"


def set_dbmovie_info(dict_request):
    """

    :param dict_request:
    :return:
    """
    info = Info.from_dict(dict_request)
    if info is None:
        return "failed, to from json"
    info.update_or_insert()
    return 'Success'


def get_info(request_str):
    try:
        douban_id, imdb_id = request_str.split('|', 1)
    except Exception as err:
        print(err)
        Log.exec_log("failed to split:" + request_str)
        return "failed:error requeststr:" + request_str
    info = Info(douban_id, imdb_id)
    if info.douban_status != OK:
        info.douban_status = RETRY
        info.douban_detail()
    return f"{info.douban_id}|{info.imdb_id}|{info.douban_score}|{info.imdb_score}|\
                {info.movie_name}|{info.nation}|{info.type}|{info.director}|{info.actors}|{info.poster}|{info.genre}"


def set_remark(request):
    """
    dict:request
    
    """
    douban_id = request.get("douban_id", "")
    imdb_id   = request.get("imdb_id", "")
    remark    = request.get("remark", "")
    if douban_id == "" and imdb_id == "":
        return "id is null"
    info = Info(douban_id, imdb_id)
    if not info.select():
        return "table info have no record"
    info.remark = remark
    if not info.update():
        return "failed to update table info"
    return "Success"


def query_movies(request):
    """
    通过json_request获取where语句的条件，查询movies表获取符合条件的记录并返回
    :param : 词典:json_request
    :return: 符合条件的记录组装json_array并dumps返回
    """
    print(request)

    where_sql = ""
    
    name = request.get('name')
    if name is not None:
        where_sql = f"movies.dirname like '%{name}%'"
    
    number = request.get('number')
    if number is not None:
        number = number.replace(" ", "")
        if where_sql != "":
            where_sql += ' and '
        if number[0:1] == ">" or number[0:1] == "<" or number[0:1] == "=":
            where_sql += f"movies.number{number}"
        else:
            where_sql += f"movies.number={number}"

    doubanid = request.get('douban_id')
    if doubanid is not None:
        if where_sql != "":
            where_sql += ' and '
        where_sql += f"movies.doubanid='{doubanid}'"

    imdbid = request.get('imdb_id')
    if imdbid is not None:
        if where_sql != "":
            where_sql += ' and '
        where_sql += f"movies.imdbid='{imdbid}'"

    other = request.get('other')
    if other is not None:
        if where_sql != "":
            where_sql += ' and '
        where_sql += other

    deleted = request.get('deleted')
    if deleted is not None:
        if where_sql != "":
            where_sql += ' and '
        if deleted == 0:
            where_sql += 'movies.deleted=0'
        else:
            where_sql += 'movies.deleted=1'

    nation = request.get('nation')
    viewed = request.get('viewed')
    genre = request.get('genre')
    remark = request.get('remark')
    if nation is not None or viewed is not None or genre is not None or remark is not None:
        select_sql = "select movies.number, movies.copy, movies.dirname, movies.disk, movies.size, \
                            movies.deleted, movies.doubanid, movies.imdbid from movies,info "
        if where_sql != "":
            where_sql += ' and '
        where_sql += "movies.doubanid=info.doubanid and movies.imdbid=info.imdbid "

        if genre is not None:
            where_sql += f" and info.genre like '%{genre}%'"
        
        if remark is not None:
            if remark != "":
                where_sql += f" and info.remark like '%{remark}%'"
            else:
                where_sql += f" and info.remark = '' "

        if nation is not None:
            if nation == "国港台":
                where_sql += " and (info.nation='港' or info.nation ='国' or info.nation='台')"
            elif nation == "韩":
                where_sql += " and info.nation='韩'"
            elif nation == '日':
                where_sql += " and info.nation='日'"
            elif nation == '英美':
                where_sql += " and (info.nation='美' or info.nation='英')"
            else:
                Log.error_log("unknown nation in query_movies:" + nation)
                return "failed"

        if viewed is not None:
            if viewed == 1: 
                where_sql += " and info.viewed=1"
            else:
                where_sql += " and info.viewed=0"
    else:
        select_sql = "select movies.number, movies.copy, movies.dirname, movies.disk, movies.size, \
                            movies.deleted, movies.doubanid, movies.imdbid from movies "

    records = select(select_sql+'where '+where_sql, None)
    print(select_sql+'where '+where_sql)
    if records is None:
        return "failed"
    dict_list = []
    for record in records:
        # print(record)
        info = Info(record[6], record[7])
        douban_score = info.douban_score if info.douban_score != "" else "-"
        imdb_score = info.imdb_score if info.imdb_score != "" else "-"
        temp_dict = {
            'number': record[0],
            'copy': record[1],
            'dir_name': record[2],
            'disk': record[3],
            'size': record[4],
            'deleted': record[5],
            'viewed': info.viewed,
            'remark': info.remark,
            'score': f"{douban_score}/{imdb_score}"
        }
        dict_list.append(temp_dict)
    return json.dumps(dict_list)


def del_movie(request):
    number = request.get('number')
    copy = request.get('copy', 0)
    size = request.get('size')
    if delete("delete from movies where number=%s and copy=%s and size=%s", (number, copy, size)):
        return "Success"
    else:
        return "failed"


def query_dbmovie_detail(request):
    number = request.get('number')
    copy = request.get('copy', 0)
    size = request.get('size')
    
    # 获取doubanid,imdbid
    records = select("select doubanid,imdbid from movies where number=%s and copy=%s and size=%s", (number, copy, size))
    if records is None or len(records) != 1:
        Log.exec_log(f"failed to exec:select doubanid,imdbid from movies "
                     f"where number={number} and copy={copy} and size={size}")
        return "failed"
    doubanid = records[0][0]
    imdbid = records[0][1]

    # 根据doubanid/imdbid获取影片详情
    info = Info(doubanid, imdbid)
    if info.movie_name == "":
        Log.exec_log(f"there is no record in info:{doubanid}|{imdbid}, so try to douban_detail")
        if doubanid != "":
            if not info.douban_detail():
                return "failed"
        else:
            return "failed"

    # 获取关联记录:number相同
    dict_list = []
    records = select("select number, dirname, disk, size, deleted from movies where number=%s ", (number,))
    if records is not None:
        for record in records:
            if record[3] != size:
                temp_dict = {
                    'number': record[0],
                    'dirname': record[1],
                    'disk': record[2],
                    'size': record[3],
                    'deleted': record[4],
                    'viewed': info.viewed
                }
                dict_list.append(temp_dict)

    # 返回结果
    result = {
        'info': info.to_dict(),
        'dbmovie_list': dict_list
    }
    return json.dumps(result)


def set_dbmovie_id(dict_request):
    """
    set dbmovie_id
    :param dict_request:
    :return:
    Success
    failed...
    """
    number = dict_request.get("number", -1)
    douban_id = dict_request.get("douban_id", "")
    imdb_id = dict_request.get("imdb_id", "")
    if number == -1 or (douban_id == "" and imdb_id == ""):
        return f"failed, invalid argument, number:{number}, douban_id:{douban_id}, imdb_id:{imdb_id}"

    if not update("update movies set doubanid=%s, imdbid=%s where number=%s", (douban_id, imdb_id, number)):
        return "failed, update movies set id"

    info = Info(douban_id, imdb_id)
    if info.douban_status != OK:
        if not info.douban_detail():
            Log.exec_log(f"failed to douban_detail:{douban_id, imdb_id}")
            return "failed, can't douban_detail"
    return "Success"


def set_viewed(dict_request):
    douban_id = dict_request.get("douban_id", "")
    imdb_id = dict_request.get("imdb_id", "")
    if douban_id == "" and imdb_id == "":
        return "failed"
    if update("update info set viewed=1 where doubanid=%s and imdbid=%s", (douban_id, imdb_id)):
        return "Success"
    else:
        return "failed"


def check_douban_cookie():
    """
    检查豆瓣cookie是否失效
    方法:tt2599106如果没有登录的情况下，是不能获取到douban_id的，所以据此可以判断cookie是否失效
    返回：
    failed: 失效
    Success: 有效
    """
    douban_id = Info.get_douban_id_by_imdb_id("tt2599106")
    if douban_id == "":
        return "failed"
    return "success"


def backup_daily():
    """
    1,把QB和TR的torrents备份到相应目录
    2, exec backup_daily.sh
        a,data/
        c,table:movies
        d,table:rss
        e,ta:info
    """
    if SysConfig.QB_BACKUP_DIR[-1:] != '/':
        SysConfig.QB_BACKUP_DIR = SysConfig.QB_BACKUP_DIR+'/'
    if SysConfig.TR_BACKUP_DIR[-1:] != '/':
        SysConfig.TR_BACKUP_DIR = SysConfig.TR_BACKUP_DIR+'/'
    if SysConfig.QB_TORRENTS_BACKUP_DIR[-1:] != '/':
        SysConfig.QB_TORRENTS_BACKUP_DIR = SysConfig.QB_TORRENTS_BACKUP_DIR+'/'
    if SysConfig.TR_TORRENTS_BACKUP_DIR[-1:] != '/':
        SysConfig.TR_TORRENTS_BACKUP_DIR = SysConfig.TR_TORRENTS_BACKUP_DIR+'/'

    # 1，backup QB的torrents目录
    if mylib.copy(SysConfig.QB_BACKUP_DIR, SysConfig.QB_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        Log.exec_log(f"success exec:copy({SysConfig.QB_BACKUP_DIR},{SysConfig.QB_TORRENTS_BACKUP_DIR})")
    else:
        Log.exec_log(f"failed to exec:copy({SysConfig.QB_BACKUP_DIR},{SysConfig.QB_TORRENTS_BACKUP_DIR})")
        return False

    # 2.1，backup TR的torrents目录
    if mylib.copy(SysConfig.TR_BACKUP_DIR+"torrents/", SysConfig.TR_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        Log.exec_log(f'success exec:copy({SysConfig.TR_BACKUP_DIR+"torrents/"},{SysConfig.TR_TORRENTS_BACKUP_DIR})')
    else:
        Log.exec_log(f'failed to exec:copy({SysConfig.TR_BACKUP_DIR+"torrents/"},{SysConfig.TR_TORRENTS_BACKUP_DIR})')
        return False
    # 2.2，backup TR的resume目录
    if mylib.copy(SysConfig.TR_BACKUP_DIR+"resume/", SysConfig.TR_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        Log.exec_log(f'success exec:copy({SysConfig.TR_BACKUP_DIR+"resume/"},{SysConfig.TR_TORRENTS_BACKUP_DIR})')
    else:
        Log.exec_log(f'failed to exec:copy({SysConfig.TR_BACKUP_DIR+"resume/"},{SysConfig.TR_TORRENTS_BACKUP_DIR})')
        return False

    """
    # 3, 执行每日备份脚本
    if os.system(SysConfig.BACKUP_DAILY_SHELL) == 0:
        exec_log(f"success exec:{SysConfig.BACKUP_DAILY_SHELL}")
    else:
        exec_log(f"failed to exec:{SysConfig.BACKUP_DAILY_SHELL}")
        return False
    """


def keep_torrents(disk_path):
    """
    输入:待进行保种的目录列表
    1、查找movies表，获取下载链接及hash
    2、如果下载链接不空，就取下载链接，否则通过hash值去种子备份目录寻找种子文件
    3、加入qb，设置分类为'转移',跳检，不创建子文件夹
    """
    global gTorrents

    pt_client = PTClient("TR")
    if not pt_client.connect():
        return "failed to connect TR"

    print(disk_path)
    dir_name_list = gTorrents.check_disk(disk_path)  # 检查tDiskPath,获取未保种的目录列表
    for dir_name in dir_name_list:
        Log.exec_log("begin to keep torrent:" + dir_name['DirPath'] + dir_name['DirName'])
        t_movie = movie.Movie(dir_name['DirPath'], dir_name['DirName'])
        if not t_movie.check_dir_name():
            Log.exec_log("failed to checkdirname:" + t_movie.dir_name)
            continue
        if not t_movie.get_torrent():
            Log.exec_log("can't get torrent:" + dir_name['DirName'])
            continue
        torrent = pt_client.add_torrent(torrent_hash="",
                                        download_link=t_movie.download_link,
                                        torrent_file=t_movie.torrent_file,
                                        download_dir=SysConfig.TR_KEEP_DIR,
                                        is_paused=True)
        if torrent is not None:
            Log.exec_log("success add torrent to tr")
        else:
            Log.error_log("failed to add torrent:" + t_movie.torrent_file + "::" + t_movie.download_link)
            continue
        t_link = os.path.join(SysConfig.TR_KEEP_DIR, torrent.name)
        t_full_path_dir_name = os.path.join(dir_name['DirPath'] + dir_name['DirName'])
        if os.path.exists(t_link):
            os.remove(t_link)
        try:    
            os.symlink(t_full_path_dir_name, t_link)
        except Exception as err:
            print(err)
            Log.error_log("failed create link:ln -s " + t_full_path_dir_name + " " + t_link)
        else:
            Log.exec_log("create link: ln -s " + t_full_path_dir_name + " " + t_link)

    # 把新加入的种子加入列表
    gTorrents.check_torrents("TR")
    return "completed"


def check_upload_limit():
    """
    检查一下是否需要进行/解除upload_limit
    当上传速度达到5M以上时进行限制，当上传速度低于4M时解除限制
    """
    # 获取qb/tr的上传速度
    qb_up_speed = PTClient.get_up_speed("QB")
    tr_up_speed = PTClient.get_up_speed("TR")
    total_speed = qb_up_speed + tr_up_speed
    # 限制状态下，如果速度低于4000KB/s 则进行解除
    if gTorrents.upload_limit_state:
        if total_speed <= 4000:
            gTorrents.set_upload_limit(-1)
            Log.exec_log("解除上传速度限制")
            gTorrents.upload_limit_state = False
    else:
        if total_speed >= 5000:
            gTorrents.set_upload_limit(200)
            Log.exec_log("开始上传速度限制(每个种子200KB/s)")
            gTorrents.upload_limit_state = True


def thread_listen_socket():
    while True:
        # 监听Client是否有任务请求
        if not gSocket.accept():
            continue

        request = gSocket.receive()
        if request == "":
            Log.socket_log("empty request")
            continue
        Log.socket_log("recv:"+request)

        reply = handle_task(request)
        # Print("begin send")
        gSocket.send(reply)
        if request.startswith('torrents') or request.startswith('log'):
            pass   # not write reply in log
        else:
            Log.socket_log("send:"+reply)
        gSocket.close()


def thread_pt_monitor():
    global gLastCheckDate

    loop_times = 0
    while True:
        loop_times += 1
        Log.log_print("loop times :" + str(loop_times % 120))

        today = datetime.datetime.now().strftime('%Y-%m-%d')

        # RSS和FREE种子订阅及查找
        gTorrents.request_torrents_from_rss_by_time(loop_times)
        gTorrents.request_torrents_from_page_by_time(loop_times)

        if today != gLastCheckDate:  # new day
            gTorrents.count_upload("QB")
            gTorrents.count_upload("TR")
            gTorrents.write_pt_backup()
            gTorrents.tracker_data()  # tracker_data执行要在count_upload()之后，这样才有新的记录
            gTorrents.count_upload_traffic()
            gTorrents.check_disk(SysConfig.CHECK_DISK_LIST)
            backup_daily()
            # 一月备份一次qb，tr,data
            if today[8:10] == '01':
                os.system(SysConfig.BACKUP_MONTHLY_SHELL)
                Log.exec_log(f"exec:{SysConfig.BACKUP_MONTHLY_SHELL}")
            if today[8:10] == '01' or today[8:10] == '15':
                update_viewed(True)  # 半月更新一次viewed
        else:
            if loop_times % 5 == 0:
                gTorrents.check_torrents("QB")

        # gLastCheckDate = datetime.datetime.now().strftime("%Y-%m-%d")
        gLastCheckDate = today
        gTorrents.last_check_date = gLastCheckDate
        Log.debug_log("update gLastCheckDate=" + gLastCheckDate)

        # 检查一下内存占用
        memory = psutil.virtual_memory()
        Log.debug_log("memory percent used:" + str(memory.percent))
        if memory.percent >= 95:
            Log.exec_log("memory percent used:" + str(memory.percent))
            PTClient("QB").restart()

        # 检查下是否要进行限制/解除上传速度
        if loop_times % 10 == 0:
            check_upload_limit()

        time.sleep(60)


if __name__ == '__main__':
    # SysConfig.os_type = platform.system()
    global SysConfig
    Log.log_clear()

    #
    SysConfig.load_sys_config("config/sys.json")
    SysConfig.load_site_config("config/site.json")
    Sites.load(SysConfig.SITE_LIST)
    # TODO 调测用traffic.txt，同步tracker_list运行一段时间
    Sites.read_tracker_data_backup("data/traffic.txt")

    # 初始化，建立torrents对象
    gTorrents = Torrents()
    Log.exec_log("begin check_torrents(QB)")
    if gTorrents.check_torrents("QB") == -1:
        exit()
    Log.exec_log("begin check_torrents(TR)")
    if gTorrents.check_torrents("TR") == -1:
        exit()
    Log.exec_log("write_pt_backup")
    gTorrents.write_pt_backup()
    
    # 初始化Socket对象
    socket.setdefaulttimeout(60)
    gSocket = Socket()
    if not gSocket.init():
        exit()
   
    gLastCheckDate = gTorrents.last_check_date
    thread_socket = threading.Thread(target=thread_listen_socket)
    Log.exec_log("begin thread_socket")
    thread_socket.start()

    thread_monitor = threading.Thread(target=thread_pt_monitor)
    Log.exec_log("begin thread_monitor")
    thread_monitor.start()

    while True:
        if not thread_socket.is_alive():
            print("restart thread_socket")
            thread_socket = threading.Thread(target=thread_listen_socket)
            thread_socket.start()
        if not thread_monitor.is_alive():
            print("restart thread_pt_monitor")
            thread_monitor = threading.Thread(target=thread_pt_monitor)
            thread_monitor.start()
        time.sleep(60)
