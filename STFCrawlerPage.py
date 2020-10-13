from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import re
import requests
import os


class STFCrawlerPage:

    def __init__(self, config_data):

        self.config_data = config_data
     

        self.chrome_driver_options = self._get_chrome_driver_options() 
        

        
  
        # get_soup_from_process_number(self.rows_current_lote[0]["processo"]))
    def _get_chrome_driver_options(self):    
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')

        return chrome_options


    def set_current_process_number(self,process_number):
        self.current_process_number = self._get_only_numbers(process_number)


    def set_soup_from_current_process_number(self):

       
        browser_crawler = webdriver.Chrome(
            chrome_options = self.chrome_driver_options,
            executable_path = self.config_data["chromeDriver"]
        )

        url_to_search =  self.config_data["url_STF"] + self.current_process_number

        browser_crawler.get(url_to_search)
        page_content = browser_crawler.page_source
        page_soup = BeautifulSoup(page_content)

        self.current_soup = page_soup


    def _get_only_numbers(self,text):
        text_only_numbers = re.sub(r'[^\d]','',text)

        return text_only_numbers


    def save_documents_from_current_soup_on_disk(self):
 
        folder_to_save = r'DOCS\{}'.format(self.current_process_number)
        os.mkdir(folder_to_save)

        for document_div in self.current_soup.findAll('div',attrs={'class':'andamento-item'}):
            for document_a in document_div.findAll('a',href=True):
     
                document_href = document_a['href']
                document_extension = re.search('=\.?(\w+)$',document_href).group(1)   
                document_name  = re.sub(r'[\n\t]','',document_a.text).strip()  
                document_number = re.sub(r'[^\d]','',document_href)

                request_document = requests.get(self.config_data["url_docs"] + document_href)

                document_file_path = folder_to_save + '/' + document_name + document_number + '.' + document_extension

                with open(document_file_path, 'wb') as file_to_save:
                    file_to_save.write(request_document.content)
                    

    def get_partes_from_current_soup(self):
        partes = []
    
        partes_div  = self.current_soup.find('div', attrs={'id':'todas-partes'})

        for parte in partes_div.findAll('div',attrs={'class':'processo-partes lista-dados'}):

            detalhe = parte.find('div', attrs={'class','detalhe-parte'})
            nome = parte.find('div', attrs={'class','nome-parte'})

            if detalhe is None or nome is None :
                continue
        
            partes.append({'detalhe' : detalhe.text , 'nome' : nome.text})

        return partes    

    def get_andamentos_from_current_soup(self):
        andamentos = []

        andamentos_div = self.current_soup.find('div', attrs={'id':'andamentos'})

        for andamento in andamentos_div.findAll('div',attrs={'class':'andamento-detalhe'}):
            data = andamento.find('div', attrs={'class','andamento-data'})
            texto = andamento.find('div', attrs={'class','col-md-9 p-0'})
            titulo = andamento.find('div', attrs={'class','col-md-5 p-l-0'})

            if data is None or texto is None or titulo is None:
                continue
            andamentos.append({'data':data.text, 'texto': texto.text, 'titulo': titulo.text.replace('\n','')})

        return andamentos

    def get_decisoes_from_current_soup(self):
        decisoes = []

        decisoes_div = self.current_soup.find('div', attrs={'id':'decisoes'})

        for decisao in decisoes_div.findAll('div',attrs={'class':'andamento-detalhe'}):
            data = decisao.find('div', attrs={'class','andamento-data'})
            texto = decisao.find('div', attrs={'class','col-md-9 p-0'})
            titulo = decisao.find('div', attrs={'class','col-md-5 p-l-0'})

            if data is None or texto is None or titulo is None:
                continue


            decisoes.append({'data':data.text, 'texto': texto.text, 'titulo': titulo.text.replace('\n','')})

        return decisoes

    


    

