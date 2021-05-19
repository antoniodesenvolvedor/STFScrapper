import psycopg2


conn = psycopg2.connect(
    host="localhost",
    database="WebScraping",
    user="postgres",
    password="labs")

cur = conn.cursor()

sql = 'select * from base'

cur.execute(sql)



conn.commit()
cur.close()
conn.close()