import mysql.connector
from log import *

DB_LOGIN = {'username': 'dummy', 'password': 'moonbeam', 'db_name': 'db_movies'}


def compose_sql(sql, val):
    """把val填入sql组装sql语句"""

    if val is None or len(val) == 0: return sql

    i = -1
    for i in range(len(val)):
        sql = sql.replace('%s',str(val[i]),1)

    if i != len(val) -1: ErrorLog("error sql:{}|{}".format(sql,val))
    return sql

def select_by_update(sql,val):
    """
    根据update语句，组装select语句，获取update之前数据库的值
    例如:
    update movies set doubanid=%s,imdbid=%s where number=%s and copy=%s (arv1,arv2,argv3,argv4)
    select doubanid,imdbid from movies where number=arv3 and copy=argv4
    """
    tNewSQL = "select "
    sql = sql.lower()
    #remove update
    tIndex = sql.find("update")
    sql = sql[tIndex+6:]
    #get table name
    tIndex = sql.find("set")
    tTableName = sql[:tIndex].strip()
    sql = sql[tIndex+3:]
    
    tIndex = sql.find("where")
    if tIndex == -1: ErrorLog("warning:no where in update sql:"+sql); return False
    tUpdateSQL = sql[:tIndex]
    tWhereSQL = sql[tIndex:]
    tColumnList=[]
    i = 0
    while True:
        tIndex = tUpdateSQL.find("=")
        if tIndex == -1 : break
        tColumnList.append(tUpdateSQL[:tIndex].strip())
        tIndex = tUpdateSQL.find(",")
        if tIndex >= 0:
            if tUpdateSQL[:tIndex].find('%s') >= 0: i += 1
        else:
            if tUpdateSQL.find('%s') >= 0: i += 1
            break
        tUpdateSQL = tUpdateSQL[tIndex+1:]

    tNewSQL = tNewSQL+','.join(tColumnList)+' from '+tTableName+' '+tWhereSQL
    database_log(compose_sql(tNewSQL,val[i:]))
    tResult = select(tNewSQL,val[i:])
    if tResult == None : return False
    for tValue in tResult:
        tString = ""
        for i in range(len(tValue)):
            tString += "{}|".format(tValue[i])
        database_log(tString)
    return True
        
def update(mSQL,mValue):

    select_by_update(mSQL,mValue)   #update之前先select获取update之前的值
    tMyDB = None
    try:
        tMyDB = mysql.connector.connect(host="localhost", user=DB_LOGIN['username'], passwd=DB_LOGIN['password'], database=DB_LOGIN['db_name'])
        tMyCursor = tMyDB.cursor()
        if mValue == None:
            tMyCursor.execute(mSQL)
        else:
            tMyCursor.execute(mSQL,mValue)
        tMyDB.commit()
    except Exception as err:
        print(err)
        #database_log(err)
        ErrorLog("error:"+compose_sql(mSQL,mValue))
        if tMyDB != None: tMyDB.close()
        return False
    else:
        database_log(compose_sql(mSQL,mValue))
        tMyDB.close()
        return True

def insert(mSQL,mValue):
    tMyDB = None
    try:
        tMyDB = mysql.connector.connect(host="localhost", user=DB_LOGIN['username'], passwd=DB_LOGIN['password'], database=DB_LOGIN['db_name'])
        tMyCursor = tMyDB.cursor()
        tMyCursor.execute(mSQL,mValue)
        tMyDB.commit()
    except Exception as err:
        print(err)
        if tMyDB != None: tMyDB.close()
        #database_log(err)
        ErrorLog("error:"+compose_sql(mSQL,mValue))
        print("failed to exec:"+mSQL)
        return False
    else:
        database_log(compose_sql(mSQL,mValue))
        tMyDB.close()
        return True

def select(mSQL,mValue=None):
    tMyDB = None
    try:
        tMyDB = mysql.connector.connect(host="localhost", user=DB_LOGIN['username'], passwd=DB_LOGIN['password'], database=DB_LOGIN['db_name'])
        tMyCursor = tMyDB.cursor()
        if mValue == None:
            tMyCursor.execute(mSQL)
        else:
            tMyCursor.execute(mSQL,mValue)
        tSelectResult = tMyCursor.fetchall()
    except Exception as err:
        print(err)
        #database_log(err)
        if tMyDB != None: tMyDB.close()
        ErrorLog("error to exec:"+mSQL)
        return None
    else:
        tMyDB.close()
        return tSelectResult
