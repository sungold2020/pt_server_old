import mysql.connector
from log import *

global g_config


def compose_sql(sql, val):
    """把val填入sql组装sql语句"""
    if val is None or len(val) == 0:
        return sql

    i = -1
    for i in range(len(val)):
        sql = sql.replace('%s', str(val[i]), 1)

    if i != len(val) - 1:
        error_log("error sql:{}|{}".format(sql, val))
    return sql


def select_by_update(sql, val):
    """
    根据update语句，组装select语句，获取update之前数据库的值
    例如:
    update movies set doubanid=%s,imdbid=%s where number=%s and copy=%s (arv1,arv2,argv3,argv4)
    select doubanid,imdbid from movies where number=arv3 and copy=argv4
    """
    t_new_sql = "select "
    sql = sql.lower()
    # remove update
    t_index = sql.find("update")
    sql = sql[t_index + 6:]
    # get table name
    t_index = sql.find("set")
    t_table_name = sql[:t_index].strip()
    sql = sql[t_index + 3:]

    t_index = sql.find("where")
    if t_index == -1:
        error_log("warning:no where in update sql:" + sql)
        return False
    t_update_sql = sql[:t_index]
    t_where_sql = sql[t_index:]
    t_column_list = []
    i = 0
    while True:
        t_index = t_update_sql.find("=")
        if t_index == -1:
            break
        t_column_list.append(t_update_sql[:t_index].strip())
        t_index = t_update_sql.find(",")
        if t_index >= 0:
            if t_update_sql[:t_index].find('%s') >= 0:
                i += 1
        else:
            if t_update_sql.find('%s') >= 0:
                i += 1
            break
        t_update_sql = t_update_sql[t_index + 1:]

    t_new_sql = t_new_sql + ','.join(t_column_list) + ' from ' + t_table_name + ' ' + t_where_sql
    database_log(compose_sql(t_new_sql, val[i:]))
    t_result = select(t_new_sql, val[i:])
    if t_result is None:
        return False
    for t_value in t_result:
        t_string = ""
        for i in range(len(t_value)):
            t_string += "{}|".format(t_value[i])
        database_log(t_string)
    return True


def update(sql, value):
    select_by_update(sql, value)  # update之前先select获取update之前的值
    t_my_db = None
    try:
        t_my_db = mysql.connector.connect(host="localhost",
                                          user=g_config.DB_LOGIN['username'],
                                          passwd=g_config.DB_LOGIN['password'],
                                          database=g_config.DB_LOGIN['db_name'])
        t_my_cursor = t_my_db.cursor()
        if value is None:
            t_my_cursor.execute(sql)
        else:
            t_my_cursor.execute(sql, value)
        t_my_db.commit()
    except Exception as err:
        print(err)
        # database_log(err)
        error_log("error:" + compose_sql(sql, value))
        if t_my_db is not None:
            t_my_db.close()
        return False
    else:
        database_log(compose_sql(sql, value))
        t_my_db.close()
        return True


def insert(sql, value):
    t_my_db = None
    try:
        t_my_db = mysql.connector.connect(host="localhost",
                                          user=g_config.DB_LOGIN['username'],
                                          passwd=g_config.DB_LOGIN['password'],
                                          database=g_config.DB_LOGIN['db_name'])
        t_my_cursor = t_my_db.cursor()
        t_my_cursor.execute(sql, value)
        t_my_db.commit()
    except Exception as err:
        print(err)
        if t_my_db is not None:
            t_my_db.close()
        # database_log(err)
        error_log("error:" + compose_sql(sql, value))
        print("failed to exec:" + sql)
        return False
    else:
        database_log(compose_sql(sql, value))
        t_my_db.close()
        return True


def select(sql, value=None):
    t_my_db = None
    try:
        t_my_db = mysql.connector.connect(host="localhost",
                                          user=g_config.DB_LOGIN['username'],
                                          passwd=g_config.DB_LOGIN['password'],
                                          database=g_config.DB_LOGIN['db_name'])
        t_my_cursor = t_my_db.cursor()
        if value is None:
            t_my_cursor.execute(sql)
        else:
            t_my_cursor.execute(sql, value)
        t_select_result = t_my_cursor.fetchall()
    except Exception as err:
        print(err)
        # database_log(err)
        if t_my_db is not None:
            t_my_db.close()
        error_log("error to exec:" + sql)
        return None
    else:
        t_my_db.close()
        return t_select_result
