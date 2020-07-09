import mysql.connector

DB_LOGIN = {'username':'dummy', 'password':'moonbeam', 'db_name':'db_movies'}

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
        tMyDB.close()
        return False
    else:
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
        print("failed to exec:"+mSQL)
        return False
    else:
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
        tMyDB.close()
        print("error to exec:"+mSQL)
        return None
    else:
        tMyDB.close()
        return tSelectResult
