from time import sleep, time
import undetected_chromedriver as uc
import pandas as pd
from datetime import datetime
from collections import Counter
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
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
1228517
1284077
1035559
1094891
1127165
1247802
1252800
1283222
1284301
1288910
1290858
1290890
1206594
1152216
1225249
1132392
1235494
1244004
1151582
1244467
1131559
1170173
1196974
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

# Tempo máximo (s) aguardando o arquivo aparecer na pasta após clicar em "Baixar"
TIMEOUT_DOWNLOAD = 120
EXTENSOES_TEMPORARIAS = ('.crdownload', '.tmp', '.part')

# XPaths da modal de arquivos (relativos a /html/body/div[N]/div/div/div[2]/div[2]/div/div/)
XP_FILTRO = 'div[1]/div[2]/div/div/input'
XP_BOTAO_BAIXAR = 'div[1]/div[2]/button[1]'
XP_LINHAS = 'div[2]/table/tbody/tr'

OBRAS = BASE.splitlines()
#chrome_options = Options()
#chrome_options.add_experimental_option("detach", True)


def base_modal(n):
    return f'/html/body/div[{n}]/div/div/div[2]/div[2]/div/div/'


def xp_fechar_modal(n):
    return f'/html/body/div[{n}]/div/div/div[1]/button'


def listar_pasta(pasta):
    try:
        return set(os.listdir(pasta))
    except OSError:
        return set()


def texto_alerta(chrome):
    try:
        alerta = chrome.find_element(By.ID, 'swal2-html-container')
        if alerta.is_displayed():
            return alerta.text.strip()
    except (NoSuchElementException, StaleElementReferenceException):
        pass
    return ''


def aguardar_download(pasta, arquivos_antes, chrome=None, timeout=TIMEOUT_DOWNLOAD):
    """Espera surgir um arquivo novo e completo na pasta. Retorna o nome ou None.
    Se o site exibir um alerta, espera no máximo mais 5s antes de desistir."""
    fim = time() + timeout
    alerta_visto = False
    while time() < fim:
        novos = listar_pasta(pasta) - arquivos_antes
        prontos = [f for f in novos if not f.lower().endswith(EXTENSOES_TEMPORARIAS)]
        pendentes = [f for f in novos if f.lower().endswith(EXTENSOES_TEMPORARIAS)]
        if prontos and not pendentes:
            return prontos[0]
        if chrome is not None and not novos and not alerta_visto and texto_alerta(chrome):
            alerta_visto = True
            fim = min(fim, time() + 5)
        sleep(0.5)
    return None


def texto_tabela(chrome, n):
    """Texto completo do tbody da modal em uma única chamada (None se não existir)."""
    try:
        tbody = chrome.find_element(By.XPATH, base_modal(n) + 'div[2]/table/tbody')
        return chrome.execute_script("return arguments[0].innerText;", tbody)
    except (NoSuchElementException, StaleElementReferenceException):
        return None


def filtrar_e_contar(chrome, n, texto, timeout=20):
    """Aplica o filtro na modal, espera a tabela estabilizar e retorna o valor de td[3] da 1ª linha."""
    base = base_modal(n)
    campo = WebDriverWait(chrome, timeout).until(
        EC.element_to_be_clickable((By.XPATH, base + XP_FILTRO)))
    antes = texto_tabela(chrome, n)
    campo.click()
    campo.clear()
    campo.send_keys(texto)

    # Pronto quando a tabela fica 0,5s sem mudar E (mudou em relação a antes OU já passaram 2s,
    # caso em que o filtro não alterou o resultado).
    inicio = time()
    estado = {'ultimo': antes, 'desde': inicio}

    def tabela_estavel(d):
        atual = texto_tabela(d, n)
        if atual is None:
            return False
        if atual != estado['ultimo']:
            estado['ultimo'] = atual
            estado['desde'] = time()
            return False
        estavel = time() - estado['desde'] >= 0.5
        return estavel and (atual != antes or time() - inicio >= 2)

    try:
        WebDriverWait(chrome, 8, poll_frequency=0.2).until(tabela_estavel)
    except TimeoutException:
        print(f"AVISO: a tabela não estabilizou após aplicar o filtro '{texto}'.")

    linhas = chrome.find_elements(By.XPATH, base + XP_LINHAS)
    if not linhas:
        return "0"
    colunas = linhas[0].find_elements(By.XPATH, './td')
    if len(colunas) < 3:
        return "0"
    return colunas[2].text.strip()


def selecionar_primeira_linha(chrome, n, timeout=20):
    celula = WebDriverWait(chrome, timeout).until(
        EC.element_to_be_clickable((By.XPATH, base_modal(n) + XP_LINHAS + '[1]/td[1]')))
    caixas = celula.find_elements(By.XPATH, './/input[@type="checkbox"]')
    if not caixas:
        celula.click()
        return True
    caixa = caixas[0]
    if not caixa.is_selected():
        try:
            caixa.click()
        except WebDriverException:
            chrome.execute_script("arguments[0].click();", caixa)
    if not caixa.is_selected():
        # checkbox estilizado: tenta clicar na própria célula
        celula.click()
    return caixa.is_selected()


def baixar_primeira_linha(chrome, n, pasta):
    """Seleciona a 1ª linha filtrada, clica em Baixar e espera o arquivo chegar na pasta."""
    arquivos_antes = listar_pasta(pasta)
    if not selecionar_primeira_linha(chrome, n):
        print("AVISO: o checkbox da 1ª linha não ficou marcado.")
    botao = WebDriverWait(chrome, 20).until(
        EC.element_to_be_clickable((By.XPATH, base_modal(n) + XP_BOTAO_BAIXAR)))
    botao.click()
    arquivo = aguardar_download(pasta, arquivos_antes, chrome)
    if arquivo:
        print(f"Arquivo baixado: {arquivo}")
    else:
        alerta = texto_alerta(chrome)
        print(f"FALHA: nenhum arquivo novo em {pasta}."
              + (f" Alerta do site: {alerta}" if alerta else ""))
    return arquivo


def fechar_modal(chrome, n, timeout=20):
    try:
        WebDriverWait(chrome, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xp_fechar_modal(n)))).click()
    except (TimeoutException, WebDriverException):
        print("AVISO: não foi possível fechar a modal de arquivos.")


def processar_arquivos(chrome, n, tempos):
    """Tenta baixar o CAD (006); se não houver, o levantamento (000). Retorna o status.
    Acumula em `tempos` a duração das etapas 'filtro' e 'download'."""
    def cronometrar(etapa, funcao, *args):
        t = time()
        try:
            return funcao(*args)
        finally:
            tempos[etapa] = tempos.get(etapa, 0) + time() - t

    try:
        qtd = cronometrar('filtro', filtrar_e_contar, chrome, n, "006")
        print(f"Quantidade 006: {qtd}")
        if qtd != "0":
            arquivo = cronometrar('download', baixar_primeira_linha, chrome, n, local_GEOEX2)
            status = "CAD BAIXADO NO GEOEX" if arquivo else "FALHA NO DOWNLOAD 006"
        else:
            qtd = cronometrar('filtro', filtrar_e_contar, chrome, n, "000")
            print(f"Quantidade 000: {qtd}")
            if qtd == "0":
                status = "SEM CAD NO GEOEX"
            else:
                arquivo = cronometrar('download', baixar_primeira_linha, chrome, n, local_GEOEX2)
                status = "LEVANTAMENTO BAIXADO NO GEOEX" if arquivo else "FALHA NO DOWNLOAD 000"
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
        print(f"Erro ao processar a modal de arquivos: {type(e).__name__}")
        status = "ERRO NA MODAL DE ARQUIVOS"
    fechar_modal(chrome, n)
    return status


def abrir_modal_arquivos(chrome, timeout=20):
    """Espera a modal abrir em div[5] ou div[4] (o que aparecer primeiro). Retorna o índice ou None."""
    def achar_modal(d):
        for n in (5, 4):
            campos = d.find_elements(By.XPATH, base_modal(n) + XP_FILTRO)
            if campos and campos[0].is_displayed() and campos[0].is_enabled():
                return n
        return False

    try:
        return WebDriverWait(chrome, timeout, poll_frequency=0.3,
                             ignored_exceptions=(StaleElementReferenceException,)).until(achar_modal)
    except TimeoutException:
        return None


def salvar_relatorio(caminho, mostrar=False):
    df = pd.DataFrame({'PROJETO': projeto_lista, 'TÍTULO': titulo_lista, 'STATUS': status_lista,})
    df.to_excel(caminho, index = False, header=True)
    if mostrar:
        print(df)
    return df


def formatar_duracao(segundos):
    minutos, seg = divmod(int(segundos), 60)
    horas, minutos = divmod(minutos, 60)
    return f"{horas}h {minutos:02d}m {seg:02d}s" if horas else f"{minutos}m {seg:02d}s"


def imprimir_resumo(duracao_total):
    contagem = Counter(status_lista)
    print("\n" + "=" * 50)
    print("RESUMO")
    print("=" * 50)
    print(f"Total de projetos: {len(status_lista)}")
    for status, qtd in contagem.most_common():
        print(f"  {status:.<40} {qtd:>3}")
    print(f"Tempo total: {formatar_duracao(duracao_total)}")
    print(f"Arquivos em: {local_GEOEX2}")

    pendentes = [(p, t, s) for p, t, s in zip(projeto_lista, titulo_lista, status_lista)
                 if s != "CAD BAIXADO NO GEOEX"]
    print()
    if pendentes:
        print(f"Projetos sem CAD baixado ({len(pendentes)}):")
        for projeto, titulo, status in pendentes:
            print(f"  {projeto} - {titulo} - {status}")
    else:
        print("Todos os projetos tiveram o CAD baixado.")
    print("=" * 50)


options = uc.ChromeOptions()
options.add_argument("--start-maximized")
prefs = {
    "profile.default_content_settings.popups": 0,
    "download.default_directory": local_GEOEX2,
    "download.prompt_for_download": False,
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
    chrome.execute_cdp_cmd(
        "Browser.setDownloadBehavior",
        {"behavior": "allow", "downloadPath": local_GEOEX2},
    )
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

XP_BOTAO_PESQUISAR = '/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[1]/div/div/div[2]/div[1]/div[1]/div/div/div/button'
XP_BOTAO_ARQUIVOS = '/html/body/div[2]/div/div[1]/div[3]/div[2]/div[2]/div[2]/section/div[4]/div/div/div[2]/div/div[4]/button'

inicio_execucao = time()

for x in OBRAS:
    if x == 'END':
        break
    if x == "":
        continue
    inicio_projeto = time()
    tempos = {}
    chrome.switch_to.window(window_name)
    #LIMPANDO O CAMPO DE PROJETO
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    chrome.find_element('xpath','//*[@id="inputProjetoText"]').clear()

    #ENVIANDO O NÚMERO DO PROJETO
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    chrome.find_element('xpath','//*[@id="inputProjetoText"]').send_keys(x)
    sleep(2)
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, XP_BOTAO_PESQUISAR)))
    chrome.find_element('xpath', XP_BOTAO_PESQUISAR).click()
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, XP_BOTAO_PESQUISAR)))
    sleep(1)
    TITULO = chrome.find_element('xpath','//*[@id="inputTitulo"]').get_attribute("value")
    if TITULO == '':
        alerta = chrome.find_element('xpath','//*[@id="swal2-html-container"]')
        if alerta.is_displayed:
            projeto_lista.append(x)
            titulo_lista.append("PROJETO NÃO EXISTE")
            status_lista.append("PROJETO NÃO EXISTE")
            chrome.refresh()
            continue
    WebDriverWait(chrome, 60).until(EC.element_to_be_clickable((By.XPATH, XP_BOTAO_PESQUISAR)))
    WebDriverWait(chrome, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputTitulo"]')))
    TITULO = chrome.find_element('xpath','//*[@id="inputTitulo"]').get_attribute("value")
    WebDriverWait(chrome, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputProjetoText"]')))
    PROJETO = chrome.find_element('xpath','//*[@id="inputProjetoText"]').get_attribute("value")
    chrome.switch_to.window(window_name)

    tempos['pesquisa'] = time() - inicio_projeto

    #CLICANDO EM ARQUIVOS
    try:
        chrome.find_element('xpath', XP_BOTAO_ARQUIVOS).click()
    except NoSuchElementException:
        status = "PROJETO NÃO DIRECIONADO"
    else:
        t = time()
        modal = abrir_modal_arquivos(chrome)
        tempos['modal'] = time() - t
        if modal is None:
            print("Modal de arquivos não abriu.")
            status = "PROJETO CONCLUÍDO"
            fechar_modal(chrome, 5, timeout=3)
        else:
            status = processar_arquivos(chrome, modal, tempos)

    projeto_lista.append(PROJETO)
    titulo_lista.append(TITULO)
    status_lista.append(status)
    t = time()
    salvar_relatorio(BACKUP)
    tempos['excel'] = time() - t
    tempos['total'] = time() - inicio_projeto

    etapas = ' | '.join(f"{nome} {seg:.1f}s" for nome, seg in tempos.items())
    print(f"[{len(status_lista)}] {PROJETO}: {status}  ->  {etapas}")

salvar_relatorio(FINAL, mostrar=True)
salvar_relatorio(BACKUP)
imprimir_resumo(time() - inicio_execucao)

input("\nBusca finalizada. Pressione Enter para fechar o navegador e encerrar...")
try:
    chrome.quit()
except Exception:
    pass
print("Script encerrado.")
