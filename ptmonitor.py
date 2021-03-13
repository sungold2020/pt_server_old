#!/usr/bin/python3
# coding=utf-8
import psutil

import mylib
import movie
from connect import *
from torrents import *
from config import *


def handle_task(request):
    global gTorrents

    socket_log("accept request:" + request)
    request_list = []
    dict_request = None
    # 尝试json解析
    try:
        dict_request = json.loads(request)
        task = dict_request['task']
    except json.JSONDecodeError:  # json解析失败，就按照以前方式解析
        request_list = request.split()
        if request_list is None or len(request_list) == 0:
            exec_log(f"unknown request:{request}")
            return f"failed,unknown request {request}"
        task = request_list[0].lower()
        del request_list[0]
    except Exception as err:
        print(err)
        return f"failed:{str(err)}"

    if   task == 'checkdisk'    :
        if len(request_list) > 0 : gTorrents.check_disk(request_list)
        else                    : gTorrents.check_disk(g_config.CHECK_DISK_LIST)
    elif task == 'rss'          :
        for RSSName in request_list: gTorrents.request_rss(RSSName, -1)
    elif task == 'free'     :
        if len(request_list) > 0 : gTorrents.request_free(request_list[0])
        else                    : gTorrents.request_free('MTeam')
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
    elif task == 'del_movie': return del_movie(dict_request)
    elif task == 'query_dbmovie_detail' : return query_dbmovie_detail(dict_request)
    elif task == 'set_viewed'   : return set_viewed(dict_request)
    elif task == 'set_dbmovie_info': return set_dbmovie_info(dict_request)
    elif task == 'set_dbmovie_id': return set_dbmovie_id(dict_request)
    elif task == 'douban_cookie': return check_douban_cookie()
    elif task == 'load_sys_config': return g_config.load_sys_config()
    elif task == 'load_rss_config': return g_config.load_rss_config()
    elif task == 'load_site_config': return g_config.load_site_config()
    else                        : socket_log("unknown request task:"+task); return "unknown request task"
    
    return "completed"


def get_log():
    last_lines = mylib.get_last_lines(g_config.ExecLogFile, 300)
    return "\n".join(last_lines)
    """
    if g_config.os_type == "Windows":
        # TODO
    elif g_config.os_type == "Linux":
        command = "tail -n 300 /root/pt/log/pt.log > log/temp.log"
        if os.system(command) == 0:
            socket_log("success exec:"+command)
        with open('log/temp.log', 'r') as f1:
            log_str = f1.read()
        return ''.join(log_str)
    else:
        return "failed, unknown os_type"
    """


def get_speed():
    qb_client = PTClient("QB")
    tr_client = PTClient("TR")
    if not(qb_client.connect() and tr_client.connect()):
        return "速度:未知"
    return "QB: {:.1f}M/s↓ {:.2f}M/s↑\nTR: {:.1f}M/s↓ {:.2f}M/s↑".format(
                qb_client.down_speed, qb_client.up_speed, tr_client.down_speed, tr_client.up_speed)


def get_free_space():
    free_size = mylib.get_free_size(g_config.DOWNLOAD_FOLDER)
    return "{:.0f}".format(free_size)


def set_info(request_str):
    try:
        douban_id, imdb_id, movie_name, nation, director, actors, poster, genre, type_str = request_str.split('|', 8)
    except Exception as err:
        print(err)
        exec_log("failed to split:" + request_str)
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
        exec_log("failed to split:" + request_str)
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
    douban_id = request.get("douban_id","")
    imdb_id   = request.get("imdb_id","")
    remark    = request.get("remark","")
    if douban_id == "" and imdb_id == "":
        return "id is null"
    info = Info(douban_id,imdb_id)
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
        number = number.replace(" ","")
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
                error_log("unknown nation in query_movies:" + nation)
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
            'score' : f"{douban_score}/{imdb_score}"
        }
        dict_list.append(temp_dict)
    return json.dumps(dict_list)


def del_movie(request):
    number = request.get('number')
    copy = request.get('copy',0)
    size = request.get('size')
    if delete("delete from movies where number=%s and copy=%s and size=%s",(number,copy,size)):
        return "Success"
    else:
        return "failed"

def query_dbmovie_detail(request):
    number = request.get('number')
    copy = request.get('copy',0)
    size = request.get('size')
    
    # 获取doubanid,imdbid
    records = select("select doubanid,imdbid from movies where number=%s and copy=%s and size=%s", (number, copy, size))
    if records is None or len(records) != 1:
        exec_log(f"failed to exec:select doubanid,imdbid from movies where number={number} and copy={copy} and size={size}")
        return "failed"
    doubanid = records[0][0]
    imdbid = records[0][1]

    # 根据doubanid/imdbid获取影片详情
    info = Info(doubanid, imdbid)
    if info.movie_name == "":
        exec_log(f"there is no record in info:{doubanid}|{imdbid}, so try to douban_detail")
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
            exec_log(f"failed to douban_detail:{douban_id, imdb_id}")
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
    if g_config.QB_BACKUP_DIR[-1:] != '/':
        g_config.QB_BACKUP_DIR = g_config.QB_BACKUP_DIR+'/'
    if g_config.TR_BACKUP_DIR[-1:] != '/':
        g_config.TR_BACKUP_DIR = g_config.TR_BACKUP_DIR+'/'
    if g_config.QB_TORRENTS_BACKUP_DIR[-1:] != '/':
        g_config.QB_TORRENTS_BACKUP_DIR = g_config.QB_TORRENTS_BACKUP_DIR+'/'
    if g_config.TR_TORRENTS_BACKUP_DIR[-1:] != '/':
        g_config.TR_TORRENTS_BACKUP_DIR = g_config.TR_TORRENTS_BACKUP_DIR+'/'

    # 1，backup QB的torrents目录
    if mylib.copy(g_config.QB_BACKUP_DIR, g_config.QB_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        exec_log(f"success exec:copy({g_config.QB_BACKUP_DIR},{g_config.QB_TORRENTS_BACKUP_DIR})")
    else:
        exec_log(f"failed to exec:copy({g_config.QB_BACKUP_DIR},{g_config.QB_TORRENTS_BACKUP_DIR})")
        return False

    # 2.1，backup TR的torrents目录
    if mylib.copy(g_config.TR_BACKUP_DIR+"torrents/", g_config.TR_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        exec_log(f'success exec:copy({g_config.TR_BACKUP_DIR+"torrents/"},{g_config.TR_TORRENTS_BACKUP_DIR})')
    else:
        exec_log(f'failed to exec:copy({g_config.TR_BACKUP_DIR+"torrents/"},{g_config.TR_TORRENTS_BACKUP_DIR})')
        return False
    # 2.2，backup TR的resume目录
    if mylib.copy(g_config.TR_BACKUP_DIR+"resume/", g_config.TR_TORRENTS_BACKUP_DIR, mylib.IGNORE):
        exec_log(f'success exec:copy({g_config.TR_BACKUP_DIR+"resume/"},{g_config.TR_TORRENTS_BACKUP_DIR})')
    else:
        exec_log(f'failed to exec:copy({g_config.TR_BACKUP_DIR+"resume/"},{g_config.TR_TORRENTS_BACKUP_DIR})')
        return False

    """
    # 3, 执行每日备份脚本
    if os.system(g_config.BACKUP_DAILY_SHELL) == 0:
        exec_log(f"success exec:{g_config.BACKUP_DAILY_SHELL}")
    else:
        exec_log(f"failed to exec:{g_config.BACKUP_DAILY_SHELL}")
        return False
    """

def listen_socket():
    while True:
        # 监听Client是否有任务请求
        if not gSocket.accept():
            continue

        request = gSocket.receive()
        if request == "":
            socket_log("empty request")
            continue
        socket_log("recv:"+request)

        reply = handle_task(request)
        # Print("begin send")
        gSocket.send(reply)
        if request.startswith('torrents') or request.startswith('log'):
            pass   # not write reply in log
        else:
            socket_log("send:"+reply)
        gSocket.close()


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
        exec_log("begin to keep torrent:" + dir_name['DirPath'] + dir_name['DirName'])
        t_movie = movie.Movie(dir_name['DirPath'], dir_name['DirName'])
        if not t_movie.check_dir_name():
            exec_log("failed to checkdirname:" + t_movie.dir_name)
            continue
        if not t_movie.get_torrent():
            exec_log("can't get torrent:" + dir_name['DirName'])
            continue
        torrent = pt_client.add_torrent(torrent_hash="",
                                        download_link=t_movie.download_link,
                                        torrent_file=t_movie.torrent_file,
                                        download_dir=g_config.TR_KEEP_DIR,
                                        is_paused=True)
        if torrent is not None:
            exec_log("success add torrent to tr")
        else:
            error_log("failed to add torrent:" + t_movie.torrent_file + "::" + t_movie.download_link)
            continue
        t_link = os.path.join(g_config.TR_KEEP_DIR, torrent.name)
        t_full_path_dir_name = os.path.join(dir_name['DirPath'] + dir_name['DirName'])
        if os.path.exists(t_link):
            os.remove(t_link)
        try:    
            os.symlink(t_full_path_dir_name, t_link)
        except Exception as err:
            print(err)
            error_log("failed create link:ln -s " + t_full_path_dir_name + " " + t_link)
        else:
            exec_log("create link: ln -s " + t_full_path_dir_name + " " + t_link)

    # 把新加入的种子加入列表
    gTorrents.check_torrents("TR")
    return "completed"


if __name__ == '__main__':
    g_config.os_type = platform.system()

    log_clear()

    # 初始化，建立torrents对象
    gTorrents = Torrents()
    if gTorrents.check_torrents("QB") == -1:
        exit()
    if gTorrents.check_torrents("TR") == -1:
        exit()
    gTorrents.write_pt_backup()
    
    # 初始化Socket对象
    socket.setdefaulttimeout(60)
    gSocket = Socket()
    if not gSocket.init():
        exit()
   
    gLastCheckDate = gTorrents.last_check_date
    thread_socket = threading.Thread(target=listen_socket)
    thread_socket.start()

    LoopTimes = 0
    while True:
        LoopTimes += 1
        log_print("loop times :" + str(LoopTimes % 120))

        gToday = datetime.datetime.now().strftime('%Y-%m-%d')

        # RSS和FREE种子订阅及查找
        gTorrents.request_rss("", LoopTimes)
        gTorrents.request_free("", LoopTimes)

        if gToday != gLastCheckDate:  # new day
            gTorrents.count_upload("QB") 
            gTorrents.count_upload("TR")
            gTorrents.write_pt_backup()
            gTorrents.tracker_data()                   # tracker_data执行要在count_upload()之后，这样才有新的记录
            gTorrents.check_disk(g_config.CHECK_DISK_LIST)
            backup_daily()
            # 一月备份一次qb，tr,data
            if gToday[8:10] == '01':
                os.system(g_config.BACKUP_MONTHLY_SHELL)
                exec_log(f"exec:{g_config.BACKUP_MONTHLY_SHELL}")
            if gToday[8:10] == '01' or gToday[8:10] == '15':
                update_viewed(True)    # 半月更新一次viewed
        else:
            if LoopTimes % 5 == 0:
                gTorrents.check_torrents("QB")
        
        # gLastCheckDate = datetime.datetime.now().strftime("%Y-%m-%d")
        gLastCheckDate = gToday
        gTorrents.last_check_date = gLastCheckDate
        debug_log("update gLastCheckDate=" + gLastCheckDate)

        # 检查一下内存占用
        tMem = psutil.virtual_memory()
        debug_log("memory percent used:" + str(tMem.percent))
        if tMem.percent >= 95:
            exec_log("memory percent used:" + str(tMem.percent))
            PTClient("QB").restart()

        time.sleep(60)
