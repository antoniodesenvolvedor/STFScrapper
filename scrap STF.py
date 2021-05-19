import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import psycopg2

url = 'http://portal.stf.jus.br/processos/listarProcessos.asp?numeroUnico='
urlDocs = 'http://portal.stf.jus.br/processos/'




chromeDriver = r"C:\Users\Anton\OneDrive\Estudos\python\chromedriver_win32\chromedriver"

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--no-sandbox')

conn = psycopg2.connect(
        host="localhost",
        database="WebScraping",
        user="postgres",
        password="2395678")

statusCarga = {'pendente' : 1, 'concluido' : 2, 'erro' : 3, 'executando' : 4 }

def startProgram():

    

    linhas = selectCargasLinhas()
    cur = conn.cursor()
    

    for linha in linhas:

        try:
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
            

        except NameError:
            print(NameError)
            sql = 'update processostf_lote_linha set status = %s, data_fim = now() where id_linha = %s'
            cur.execute(sql, (statusCarga['erro'],linha['id_linha']))
            conn.commit()
            

    conn.close()
 



def selectCargasLinhas():

    linhas = []

    cur = conn.cursor()
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
            and status = 1
    '''

    cur.execute(sql)
    cargas = cur.fetchall()

    for row in cargas:
        lote_carga = row[0]
        nome_lote = row[1]
        sql = 'select id_linha,id_lote,processo from processostf_lote_linha where id_lote = %s and apagado = 0 and status = 1'
        cur.execute(sql,str(lote_carga))

    
        for linha in cur.fetchall():
            linhas.append({'id_linha':linha[0],'id_lote':linha[1],'processo':linha[2]})

   
    return linhas
        


def savePartesDatabase(partes,id_linha): 
    cur = conn.cursor()
    sql = 'insert into tbl_partes (detalhe,nome,apagado,datacad,id_linha) values (%s,%s,0 ,now(),%s)'

    for parte in partes:
        cur.execute(sql, (parte['detalhe'],parte['nome'],id_linha))
    
    conn.commit()


def saveDecisoesDatabase(decisoes,id_linha): 
    cur = conn.cursor()
    sql = 'insert into tbl_decisoes (titulo,texto,data,apagado,datacad,id_linha) values (%s,%s,%s,0,now(),%s)'

    for decisao in decisoes:
        cur.execute(sql, (decisao['titulo'],decisao['texto'],decisao['data'],id_linha))
    
    conn.commit() 


def saveAndamentosDatabase(andamentos,id_linha):
    cur = conn.cursor()
    sql = 'insert into tbl_andamentos (titulo,texto,data,apagado,datacad,id_linha) values (%s,%s,%s,0 ,now(),%s)'

    for andamento in andamentos:
        cur.execute(sql,(andamento['titulo'],andamento['texto'],andamento['data'],id_linha))

    conn.commit()





def getPartes(soup):  
    partes = []
    
    todasPartes  = soup.find('div', attrs={'id':'todas-partes'})

    for parte in todasPartes.findAll('div',attrs={'class':'processo-partes lista-dados'}):

        detalhe = parte.find('div', attrs={'class','detalhe-parte'})
        nome = parte.find('div', attrs={'class','nome-parte'})

        if detalhe is None or nome is None :
            continue
    
        partes.append({'detalhe' : detalhe.text , 'nome' : nome.text})

    return partes

def getAndamentos(soup):
    andamentos = []

    painelAndamentos = soup.find('div', attrs={'id':'andamentos'})

    for andamento in painelAndamentos.findAll('div',attrs={'class':'andamento-detalhe'}):
        # print(andamento)
        data = andamento.find('div', attrs={'class','andamento-data'})
        texto = andamento.find('div', attrs={'class','col-md-9 p-0'})
        titulo = andamento.find('div', attrs={'class','col-md-5 p-l-0'})

        if data is None or texto is None or titulo is None:
            continue
        # print(data.text)
        # print(texto.text)
        # print(titulo.text)

        andamentos.append({'data':data.text, 'texto': texto.text, 'titulo': titulo.text.replace('\n','')})

    return andamentos



def getDecisoes(soup):
    decisoes = []

    painelDecisoes = soup.find('div', attrs={'id':'decisoes'})

    for decisao in painelDecisoes.findAll('div',attrs={'class':'andamento-detalhe'}):
        # print(andamento)
        data = decisao.find('div', attrs={'class','andamento-data'})
        texto = decisao.find('div', attrs={'class','col-md-9 p-0'})
        titulo = decisao.find('div', attrs={'class','col-md-5 p-l-0'})

        if data is None or texto is None or titulo is None:
            continue
        # print(data.text)
        # print(texto.text)
        # print(titulo.text)

        decisoes.append({'data':data.text, 'texto': texto.text, 'titulo': titulo.text.replace('\n','')})

    return decisoes


def getDocumentos(soup,urlDocs,processoApenasNumeros):

    pasta =  r'DOCS\{}'.format(processoApenasNumeros)
    os.mkdir( pasta)


    for bloco in soup.findAll('div',attrs={'class':'andamento-item'}):
        for doc in bloco.findAll('a',href=True):
     
            href = doc['href']
            extensao = re.search('=\.?(\w+)$',href).group(1)   
            nome  = re.sub(r'[\n\t]','',doc.text).strip()         
            numeroDoc = re.sub(r'[^\d]','',href)

      

            response = requests.get(urlDocs + href)

            with open(pasta + '/' + nome + numeroDoc + '.' + extensao, 'wb') as f:
                f.write(response.content)#
            
            #Dados completos


                


            
        
    
   

        
    
 


          

def getProcessSoup(url,chromeDriver,chrome_options):
    browser = webdriver.Chrome(chrome_options=chrome_options,executable_path=chromeDriver)
    browser.get(url)
    content = browser.page_source
    soup = BeautifulSoup(content)
    
    return soup



startProgram()



  
    


