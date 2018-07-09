import psycopg2
import sys
import tqdm
conn = None
try:
    connect_str = "dbname='mach_log' user='postgres' port=1111 host='localhost' " + \
                  "password='ZelenaSolata'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str, )
    # create a psycopg2 cursor that can execute queries
    cursor = conn.cursor()

    # create a new table with a single column called "name"
    cursor.execute("SELECT * FROM value_log where message_type = 'error' limit 100")


    count = cursor.rowcount
    print('Fetched', cursor.rowcount, 'records')
    if count == 0:
        print('No records remaining, exiting')
        sys.exit()
    rows = cursor.fetchall()
    idx = 0


    for r in tqdm.tqdm(rows):
        if r == None:
            continue
        for key in r[4]['content']:
            print(key)
            cursor.execute(
                "INSERT INTO errors(timestamp,source,thread,message,client_id) VALUES({time},'{src}','{thread}','{message}','{client}')".format(
                    time=r[1], src=key['source'], message=key['message'], client=r[2], thread=key['thread']))
        idx += 1
        cursor.execute("DELETE FROM value_log WHERE id = " + str(r[0]))
        if idx % 100 == 0:
            conn.commit()
        #print('[{}] Deleted record {}: {} rows'.format(idx, r[0], cursor.rowcount))

    conn.commit()

    cursor.close()

except Exception as e:
    conn.commit()
    cursor.close()
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)
