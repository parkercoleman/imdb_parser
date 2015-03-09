import psycopg2
import psycopg2.extras

def execute_sql(db_connection, sql, args):
    '''
    Executes whatever SQL is passed to it, with hte supplied args
    :param db_connection:
    :param sql:
    :param args:
    :return:
    '''
    e = None
    c = db_connection.cursor()
    try:
        if len(args) == 0:
            c.execute(sql)
        else:
            c.execute(sql, args)
        db_connection.commit()

    except Exception, e:
        db_connection.rollback()

    #Return the exception if there
    # is one so the calling function can do
    # something about it, if it even cares
    c.close()
    return e

def execute_sql_select(db_connection, sql, args):
    c = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if len(args) == 0:
        c.execute(sql)
    else:
        c.execute(sql, args)

    rs = c.fetchall()
    c.close()
    return rs