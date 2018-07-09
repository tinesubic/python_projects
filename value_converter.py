import psycopg2
import sys

try:
    connect_str = "dbname='mach_log' user='postgres' port=1111 host='localhost' " + \
                  "password='ZelenaSolata'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str, )
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()

    # create a new table with a single column called "name"
    cursor.execute("SELECT * FROM value_log where message_type = 'value_change' limit 100000")
    # run a SELECT statement - no data in there, but we can try it
    # cursor.execute("""SELECT * from tutorials""")

    rows = cursor.fetchall()
    cursor.fetc
    print('Fetched', len(rows), 'records')
    if len(rows) == 0:
        print('No records remaining, exiting')
        sys.exit()

    idx = 0
    for r in rows:
        for key in r[4]['content']:
            cursor.execute(
                "INSERT INTO values(timestamp,source,value,client_id) VALUES({time},'{src}','{val}','{client}')".format(
                    time=r[1], src=key, val=str(r[4]['content'][key]), client=r[2]))
        idx += 1
        cursor.execute("DELETE FROM value_log WHERE id = " + str(r[0]))
        if idx % 100 == 0:
            conn.commit()
            print("Clean commit")
        print('[{}] Deleted record {}: {} rows'.format(idx, r[0], cursor.rowcount))

    conn.commit()

    cursor.close()

except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)
