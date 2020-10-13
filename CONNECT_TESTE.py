import psycopg2


conn = psycopg2.connect(
    host="localhost",
    database="WebScraping",
    user="postgres",
    password="2395678")

cur = conn.cursor()

sql = 'insert into tbl_partes (detalhe,nome,apagado,datacad,id_linha) values (%s,%s,0 ,now(),1)'

cur.execute(sql, ('antonio','advogado'))


conn.commit()
cur.close()
conn.close()