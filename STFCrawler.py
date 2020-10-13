import psycopg2
import json
from STFCrawlerPage import STFCrawlerPage 
import time



class CrawlerSTF:

    def __init__(self):

        

        self.config_data = self.get_config_data()
        self.db_connection = self.connect_database()
        self.db_status = self.get_status_dictionary()

        self.start_crawling()


        self.current_lote = self.get_one_pending_lote()
        # self.set_status_database_current_lote(self.db_status["executing"])
        
        self.rows_current_lote = self.get_rows_current_lote()

        crawler_page = STFCrawlerPage(self.config_data["crawler"])

        crawler_page.set_current_process_number(self.rows_current_lote[0]["processo"])

        crawler_page.set_soup_from_current_process_number()

        row_id = self.rows_current_lote[0]["id_linha"]
        row_partes = crawler_page.get_partes_from_current_soup()
        row_decisoes = crawler_page.get_decisoes_from_current_soup()
        row_andamentos = crawler_page.get_andamentos_from_current_soup()
        crawler_page.save_documents_from_current_soup_on_disk()

        self.save_partes_database(row_partes,row_id)
        self.save_decisoes_database(row_decisoes,row_id)
        self.save_andamentos_database(row_andamentos,row_id)
     

       


        

    def connect_database(self):
        db_connection = psycopg2.connect(
            host=self.config_data["postgres"]["host"],
            database=self.config_data["postgres"]["database"],
            user=self.config_data["postgres"]["user"],
            password=self.config_data["postgres"]["password"])
        return db_connection
    

    def get_config_data(self):
        with open('config.json') as config_file:
            config_data = json.load(config_file)
        return config_data
    

    def get_status_dictionary(self):
        db_cursor = self.db_connection.cursor()
        sql_command = '''
            select 
                status,
                id_status            
            from 
                status
        '''
        db_cursor.execute(sql_command)
        db_status = db_cursor.fetchall()
        db_status = dict(db_status)

        return db_status
    
   
    
        
    def save_error_db(self,error_message):
        sql_command = 'INSERT INTO tbl_log_erros (datacad, texto) values (now(),%s)'

        db_cursor = self.db_connection.cursor()
        db_cursor.execute(sql_command, (error_message,))
        self.db_connection.commit()

    def get_one_pending_lote(self):
  
        db_cursor = self.db_connection.cursor()
        sql = '''
            select 
                id_lote, 
                nome_lote, 
                status, 
                data_cad, 
                data_fim, 
                user_cad 
            from 
                processostf_lote
            where
                apagado = 0
                and status = 12
            order by data_cad 
            limit(1)       
        '''

        db_cursor.execute(sql)
        processo_lote = db_cursor.fetchone()

        return processo_lote
        

    def start_current_lote_database(self):
        db_cursor = self.db_connection.cursor()
        sql_command = 'update processostf_lote set status = %s, data_fim = now() where id_lote = %s'
            
        db_cursor.execute(sql_command, (status,self.current_lote))
        self.db_connection.commit()

    def set_status_database_current_row(self,status):
        db_cursor = self.db_connection.cursor()
        sql_command = 'update processostf_lote set status = %s, data_fim = now() where id_lote = %s'
            
        db_cursor.execute(sql_command, (status,self.current_lote))
        self.db_connection.commit()

    
    def get_rows_current_lote(self):
        rows_current_lote = []

        db_cursor = self.db_connection.cursor()
        sql_command = '''
            select 
                id_linha,
                id_lote,
                processo 
            from 
                processostf_lote_linha 
            where 
                id_lote = %s 
                and apagado = 0 
                and status = 1
                '''
        db_cursor.execute(sql_command,(self.current_lote,))
 
        for row in db_cursor.fetchall():
            rows_current_lote.append({'id_linha':row[0],'id_lote':row[1],'processo':row[2]})

        return rows_current_lote


    def save_partes_database(self,partes,id_linha): 
        db_cursor = self.db_connection.cursor()
        sql_command = 'insert into tbl_partes (detalhe,nome,apagado,datacad,id_linha) values (%s,%s,0 ,now(),%s)'

        for parte in partes:
            db_cursor.execute(sql_command, (parte['detalhe'],parte['nome'],id_linha))
        
        self.db_connection.commit()


    def save_decisoes_database(self, decisoes,id_linha): 
        db_cursor = self.db_connection.cursor()
        sql_command = 'insert into tbl_decisoes (titulo,texto,data,apagado,datacad,id_linha) values (%s,%s,%s,0,now(),%s)'

        for decisao in decisoes:
            db_cursor.execute(sql_command, (decisao['titulo'],decisao['texto'],decisao['data'],id_linha))
        
        self.db_connection.commit() 


    def save_andamentos_database(self, andamentos,id_linha):
        db_cursor = self.db_connection.cursor()
        sql_command = 'insert into tbl_andamentos (titulo,texto,data,apagado,datacad,id_linha) values (%s,%s,%s,0 ,now(),%s)'

        for andamento in andamentos:
            db_cursor.execute(sql_command,(andamento['titulo'],andamento['texto'],andamento['data'],id_linha))

        self.db_connection.commit()
    
    def search_pending_lote_until_find_one(self):
        lote = self.get_one_pending_lote()

        while(lote is None):
            sleep_time = 15
            print('Não há lotes pendentes procurando novamente em {} segundos'.format(sleep_time))
            time.sleep(sleep_time)
            lote = self.get_one_pending_lote()

        return lote


    def crawling_rows(self):

        crawler_page = STFCrawlerPage(self.config_data["crawler"])

        for row in self.rows_current_lote:
            
            row_id = row["id_linha"]

            db_cursor = self.db_connection.cursor()
            sql_command = 'update processostf_lote_linha set status = %s, data_inicio_processamento = now() where id_linha = %s'   
            db_cursor.execute(sql_command, (self.db_status['executing'],row_id))
            conn.commit()

            crawler_page.set_current_process_number(row["processo"])
            crawler_page.set_soup_from_current_process_number()

      
            row_partes = crawler_page.get_partes_from_current_soup()
            row_decisoes = crawler_page.get_decisoes_from_current_soup()
            row_andamentos = crawler_page.get_andamentos_from_current_soup()

            self.save_partes_database(row_partes,row_id)
            self.save_decisoes_database(row_decisoes,row_id)
            self.save_andamentos_database(row_andamentos,row_id)
            crawler_page.save_documents_from_current_soup_on_disk()

            db_cursor = self.db_connection.cursor()
            sql_command = 'update processostf_lote_linha set status = %s, data_fim = now() where id_linha = %s'   
            db_cursor.execute(sql_command, (self.db_status['finished'],row_id))
            conn.commit()




    def start_crawling(self):

        while(True):
            lote = self.search_pending_lote_until_find_one()
            self.current_lote = lote      
            self.set_status_database_current_lote(self.db_status['executing'])

            self.rows_current_lote = self.get_rows_current_lote()

            



     



    def start_crawling_rows_current_lote(self):
        sql = 'update processostf_lote_linha set status = %s, data_inicio_processamento = now() where id_linha = %s'
        cur.execute(sql, (statusCarga['executando'],linha['id_linha']))
        conn.commit()

        processoApenasNumeros = re.sub(r'[^\d]','',linha['processo'])        
        
        urlToSearch = url + processoApenasNumeros
        soup = getProcessSoup(urlToSearch,chromeDriver,chrome_options)
    
        getDocumentos(soup,urlDocs,processoApenasNumeros)


        partes = getPartes(soup)
        savePartesDatabase(partes,linha['id_linha'])

        andamentos = getAndamentos(soup)
        saveAndamentosDatabase(andamentos,linha['id_linha'])

        decisoes = getDecisoes(soup)
        saveDecisoesDatabase(decisoes,linha['id_linha'])



        sql = 'update processostf_lote_linha set status = %s, data_fim = now() where id_linha = %s'
        cur.execute(sql, (statusCarga['concluido'],linha['id_linha']))
        conn.commit()



   



    




crawler_STF = CrawlerSTF()





            




 


