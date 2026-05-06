from time import sleep
import undetected_chromedriver as uc 
import pandas as pd
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

tempo_inicio = datetime.now().strftime("-%d")
mes_inicio = datetime.now().strftime("-%m-%Y-%H-%M-%S") 
mes_inicio2 = datetime.now().strftime("-%m-%Y") 
dia_inicio = int(tempo_inicio)
data = str(dia_inicio)+mes_inicio
data2=str(dia_inicio)+mes_inicio2

# há um erro quando o projeto está corrompido que cracha o script, precisa tratar isso depois. Ex: 746243
# 'Erro Não foi possível processar sua solicitação. Ocorreu um erro no servidor. Tente novamente. Você deseja registrar o erro e abrir um chamado para o suporte verificar?
BASE = ("""
1168706
1044471
1156408
1033772
1107693
1113369
1130035
1256575
1147939
1145462
1118880
END
""")

pc_diretorio = r'C:\Users\rodfr\OneDrive\Documentos\PYTHON'
meu_diretorio = r'G:\Drives compartilhados\FUTURO CONSTRUÇÕES\PLANEJAMENTO\DOCUMENTAÇÃO\PROJETOS'
local_diretorio = 'MAGNETICOS'+data2
relatorio_geoex = 'Relatorio-GEOEX'+data+'.xlsx'
local_diretorio2 = 'MAGNETICOS'+data2
barra = '\\'

if not os.path.exists(meu_diretorio+barra+local_diretorio2):
    os.makedirs(meu_diretorio+barra+local_diretorio2)
BACKUP = meu_diretorio+barra+local_diretorio+barra+relatorio_geoex
FINAL = pc_diretorio+barra+relatorio_geoex
local_GEOEX = meu_diretorio+barra+local_diretorio+barra
local_GEOEX2 = meu_diretorio+barra+local_diretorio2+barra
local_Chromedriver = os.path.join(os.getcwd(),r"assets\chromedriver.exe")

OBRAS = BASE.splitlines()
#chrome_options = Options()
#chrome_options.add_experimental_option("detach", True)


options = uc.ChromeOptions()
options.add_argument("--start-maximized")
prefs = {
    "profile.default_content_settings.popups": 0,
    "download.default_directory": local_GEOEX2,
    "directory_upgrade": True
}
options.add_experimental_option("prefs", prefs)
path = os.path.join(os.getcwd(),r"Geoex-Scraping\assets\chromedriver.exe")
path_casa = os.path.join(os.getcwd(),r"Geoex-Scraping\assets\chromedriver.exe")
#path = path_casa
# options.add_argument('--lang=en_US')

print("\nIniciando navegador...")
try:
    chrome = uc.Chrome(options=options,driver_executable_path=local_Chromedriver)
    print("Acessando Geoex...")
    chrome.get('https://neoex.net.br/')
except Exception as e:
    print("Erro ao iniciar o navegador ou acessar o Geoex:", e)
    exit()

input("Por favor, faça login e pressione Enter para continuar...")

try:
    chrome.get('https://neoex.net.br/#/Programacao/ConsultarProjeto')
except Exception as e:
    print("Erro ao acessar a tela de consulta de projeto:", e)
    exit()

sleep(2)
window_name=chrome.window_handles[0]
projeto_lista = []
titulo_lista = []
status_lista = []
STATUS = 0
TITULO = 0
PROJETO = 0

for x in OBRAS:
    if x == 'END':
        break
    if x == "":
        continue
    chrome.switch_to.window(window_name)
    #LIMPANDO O CAMPO DE PROJETO
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    chrome.find_element('xpath','//*[@id="inputProjetoText"]').clear()
    
    #ENVIANDO O NÚMERO DO PROJETO
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    chrome.find_element('xpath','//*[@id="inputProjetoText"]').send_keys(x)
    sleep(2)
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[1]/div/div/div[2]/div[1]/div[1]/div/div/div/button')))
    chrome.find_element('xpath','/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[1]/div/div/div[2]/div[1]/div[1]/div/div/div/button').click()
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[1]/div/div/div[2]/div[1]/div[1]/div/div/div/button')))
    sleep(1)
    TITULO = chrome.find_element('xpath','//*[@id="inputTitulo"]').get_attribute("value")
    if TITULO == '':
        alerta = chrome.find_element('xpath','//*[@id="swal2-html-container"]')
        if alerta.is_displayed:
            projeto_lista.append(x)
            titulo_lista.append("PROJETO NÃO EXISTE")
            status_lista.append("PROJETO NÃO EXISTE")
            #df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista})
            #df.to_excel(r'C:\Users\user\Desktop\ORCAMENTOS\Ekko_v.0.1\Relatorios\BACKUPS\Relatorio-DANI-16-09.xlsx', index = False, header=True)
            #print(df)
            chrome.refresh()
            continue
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[1]/div/div/div[2]/div[1]/div[1]/div/div/div/button')))
    WebDriverWait(chrome, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputTitulo"]')))
    TITULO = chrome.find_element('xpath','//*[@id="inputTitulo"]').get_attribute("value")
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    PROJETO = chrome.find_element('xpath','//*[@id="inputProjetoText"]').get_attribute("value")
    chrome.switch_to.window(window_name)
    #CLICANDO SEM ALERTA VERMELHO    
    try:
        print("entrei no primeiro try")
        #CLICANDO EM ARQUIVOS
        chrome.find_element('xpath','/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[4]/div/div/div[2]/div/div[4]/button').click()
        try:
            print("entrei no segundo try")            
            WebDriverWait(chrome, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input')))
            WebDriverWait(chrome, 20).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input')))
           # chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').click()
            chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').send_keys("006")
            WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[3]')))
            projeto_vazio = chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[3]').text
            print(projeto_vazio)
            if projeto_vazio == "0":
                print("entrei no primeiro if")
                WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input')))
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').click()
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').clear()
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').send_keys("000")
                WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[3]')))
                projeto_vazio = chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[3]').text
                if projeto_vazio == "0":
                    print("entrei no segundo if")
                    projeto_lista.append(PROJETO)
                    titulo_lista.append(TITULO)
                    status_lista.append("SEM CAD NO GEOEX")
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                    df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                    df.to_excel(BACKUP, index = False, header=True)
                    print(df)
                    continue
                else:
                    print("entrei no primeiro else")
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]').click()
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]').click()
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                    projeto_lista.append(PROJETO)
                    titulo_lista.append(TITULO)
                    status_lista.append("LEVANTAMENTO BAIXADO NO GEOEX")
                    df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                    df.to_excel(BACKUP, index = False, header=True)
                    print(df)
                    continue
            else:
                print("entrei no segundo else")
                WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]')))
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]').click()
                WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]')))
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]').click()
                WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                projeto_lista.append(PROJETO)
                titulo_lista.append(TITULO)
                status_lista.append("CAD BAIXADO NO GEOEX")
                df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                df.to_excel(BACKUP, index = False, header=True)
                print(df)
                continue
        except TimeoutException:
            print("ESSA NÃO TEM FOTO")
            try:
                WebDriverWait(chrome, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input')))
                print("entrei no segundo try")
                chrome.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').click()
                chrome.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').send_keys("006")
                WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[3]/div/div/div[2]/table/tbody/tr[1]/td[3]')))
                projeto_vazio = chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[3]/div/div/div[2]/table/tbody/tr[1]/td[3]').text
                if projeto_vazio == "0":
                    print("entrei no primeiro if")
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input')))
                    chrome.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').click()
                    chrome.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').clear()
                    chrome.find_element('xpath','/html/body/div[4]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/div/div/input').send_keys("000")
                    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[3]/div/div/div[2]/table/tbody/tr[1]/td[3]')))
                    projeto_vazio = chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[3]/div/div/div[2]/table/tbody/tr[1]/td[3]').text
                    if projeto_vazio == "0":
                        print("entrei no segundo if")
                        projeto_lista.append(PROJETO)
                        titulo_lista.append(TITULO)
                        status_lista.append("SEM CAD NO GEOEX")
                        df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                        df.to_excel(BACKUP, index = False, header=True)
                        print(df)
                        continue
                    else:
                        print("entrei no primeiro else")
                        WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]')))
                        chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]').click()
                        WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]')))
                        chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]').click()
                        WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                        chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                        projeto_lista.append(PROJETO)
                        titulo_lista.append(TITULO)
                        status_lista.append("LEVANTAMENTO BAIXADO NO GEOEX")
                        df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                        df.to_excel(BACKUP, index = False, header=True)
                        print(df)
                        continue
                else:
                    print("entrei no segundo else")
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[2]/table/tbody/tr[1]/td[1]').click()
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[2]/div[2]/div/div/div[1]/div[2]/button[1]').click()
                    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                    chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                    projeto_lista.append(PROJETO)
                    titulo_lista.append(TITULO)
                    status_lista.append("CAD BAIXADO NO GEOEX")
                    df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
                    df.to_excel(BACKUP, index = False, header=True)
                    print(df)
            except TimeoutException:
                projeto_lista.append(PROJETO)
                titulo_lista.append(TITULO)
                status_lista.append("PROJETO CONCLUÍDO")
                WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div[1]/button')))
                chrome.find_element('xpath','/html/body/div[5]/div/div/div[1]/button').click()
                continue           
    except NoSuchElementException:
        projeto_lista.append(PROJETO)
        titulo_lista.append(TITULO)
        status_lista.append("PROJETO NÃO DIRECIONADO")
        continue
    
df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
df.to_excel(FINAL, index = False, header=True)
df.to_excel(BACKUP, index = False, header=True)
print(df)
while True:
    sleep(1)