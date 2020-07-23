import mysql.connector
from log import *

DB_LOGIN = {'username':'dummy', 'password':'moonbeam', 'db_name':'db_movies'}

def compose_sql(sql,val):

    if val == None or len(val) == 0 : return sql

    for i in range(len(val)):
        sql = sql.replace('%s',str(val[i]),1)

    if i != len(val) -1: database_log("error sql:{}|{}".format(sql,val))
    return sql

def update(mSQL,mValue):
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
        database_log(err)
        database_log("error:"+compose_sql(mSQL,mValue))
        tMyDB.close()
        return False
    else:
        database_log(compose_sql(mSQL,mValue))
        tMyDB.close()
        return True


def insert(mSQL,mValue):
    try:
        tMyDB = mysql.connector.connect(host="localhost", user=DB_LOGIN['username'], passwd=DB_LOGIN['password'], database=DB_LOGIN['db_name'])
        tMyCursor = tMyDB.cursor()
        tMyCursor.execute(mSQL,mValue)
        tMyDB.commit()
    except Exception as err:
        print(err)
        tMyDB.close()
        database_log(err)
        database_log("error:"+compose_sql(mSQL,mValue))
        print("failed to exec:"+mSQL)
        return False
    else:
        database_log(compose_sql(mSQL,mValue))
        tMyDB.close()
        return True

def select(mSQL,mValue):
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
        database_log(err)
        tMyDB.close()
        print("error to exec:"+mSQL)
        return None
    else:
        tMyDB.close()
        return tSelectResult
