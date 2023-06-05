from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from argparse import ArgumentParser
from getpass import getpass
import glob
import time 
import csv

def argumentos(parser = ArgumentParser()):
    parser.add_argument( "-user", "--user", type = str, help = "Usuário do twitter")
    parser.add_argument( "-password", "--password", type = str, help = "Senha do twitter")
    parser.add_argument( "-email", "--email", type = str, help = "Email da conta do twitter (caso seja necessário autenticação)")
    parser.add_argument( "-mes", "--mes", type=str, help = "Mês de coleta dos tweets no ano de 2023")
    return parser

def get_periodo(mes):
    if mes == 'janeiro':
        de = '2023-01-01'
        ate = '2023-01-31'
    if mes == 'fevereiro':
        de = '2023-02-01'
        ate = '2023-02-28'
    if mes == 'marco':
        de = '2023-03-01'
        ate = '2023-03-31'
    if mes == 'abril':
        de = '2023-04-01'
        ate = '2023-04-30'
    if mes == 'maio':
        de = '2023-05-01'
        ate = '2023-05-31'
    return de, ate

def realizaLogin(usuario, email, senha, chrome_driver):
    #   Realiza login
    chrome_driver.get('https://twitter.com/i/flow/login')
    email_conta = WebDriverWait(chrome_driver, 20).until( 
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))
    )
    email_conta.send_keys(email)

    botao_login = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]')
    chrome_driver.execute_script("arguments[0].click();", botao_login)
  
    user_conta = WebDriverWait(chrome_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="text"]'))
    )
    user_conta.send_keys(usuario)

    botao_verificacao = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div')
    chrome_driver.execute_script("arguments[0].click();", botao_verificacao)

    senha_conta = WebDriverWait(chrome_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[name="password"]'))
    )
    senha_conta.send_keys(senha)

    botao_login_2 = chrome_driver.find_element(By.XPATH,'/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div')
    chrome_driver.execute_script("arguments[0].click();", botao_login_2)

def get_texto_e_emojis(elemento):
    texto = ''
    childs = elemento.find_elements(By.XPATH,'./*')
    for c in childs:
        #print(c.tag_name)
        if(c.tag_name == 'img'):
            emoji = c.get_attribute("alt")
            texto = texto+emoji
        else:
            texto = texto + c.text
            #print(c.text)
    return texto

def get_dados_tweet(tweet):
    try:
        # Nome no Twitter
        nome = tweet.find_element(By.XPATH,'.//span').text 
        #print("Nome: " + nome)
        
        # User
        usuario = tweet.find_element(By.XPATH,'.//span[contains(text(),"@")]').text 
        #print("User: " + usuario)
        
        # Data de publicação
        dataPublicacao = tweet.find_element(By.XPATH,'.//time').get_attribute('datetime')
        #print("Data de publicação: " + dataPublicacao)
        
        # ID do Tweet
        idTweet = tweet.find_element(By.XPATH,f'.//div[@data-testid="User-Name"]/div[2]/div/div[3]/a').get_attribute('href')
        #print("ID: " + idTweet)
        
        texto = get_texto_e_emojis(tweet.find_element(By.XPATH, './/div[2]/div[2]/div[2]/div'))
        if not texto:
            texto = ''
        #print("Tweet: " + texto)
        
        # Quantidade de replies
        replies = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="reply"]').text
        if not replies:
            replies = '0'
        # Quantidade de retweets ou quotes 
        retweets = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="retweet"]').text
        if not retweets:
            retweets = '0'
        # Quantidade de likes 
        likes = tweet.find_element(By.CSS_SELECTOR,'div[data-testid="like"]').text
        if not likes:
            likes = '0'
    except:
        return
    #print("Likes: " + likes + "\t" + "Replies: " + replies + "\t"+ "Retweets: " + retweets + "\n")
    
    dados = (nome,usuario,idTweet,dataPublicacao,texto,replies,retweets,likes)
    return dados

def buscaTweets(listaUsuarios, mes, chrome_driver):
    caixa_pesquisa = WebDriverWait(chrome_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input'))
    )
    body = WebDriverWait(chrome_driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body'))
    )
    i = 0
    de, ate = get_periodo(mes)
    for usuario in listaUsuarios:
        i = i+1
        print('Usuario',i, 'de',len(listaUsuarios), f'@{usuario}')

        caixa_pesquisa.send_keys(Keys.CONTROL + "a")
        caixa_pesquisa.send_keys('(from:'+usuario+') until:'+ate+' since:'+de+' -filter:replies')
        caixa_pesquisa.send_keys(Keys.RETURN)

        aba_mais_recentes = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/main/div/div/div/div[1]/div/div[1]/div[1]/div[2]/nav/div/div[2]/div/div[2]/a'))   
        )
        chrome_driver.execute_script("arguments[0].click();", aba_mais_recentes)

        dados = []
        tweet_ids = set()
        posicao_final = chrome_driver.execute_script("return window.pageYOffset;")
        rolagem = True

        while rolagem:
            try:
                if WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))):
                    tweets = chrome_driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            except:
                tweets = []
            if len(tweets) > 0:
                for t in tweets:
                    dados_tweet = get_dados_tweet(t)
                    if dados_tweet:
                        tweet_id = dados_tweet[2]
                        if tweet_id not in tweet_ids:
                            tweet_ids.add(tweet_id)
                            dados.append(dados_tweet)
            else:
                # Nenhum tweet encontrado
                dados = [('','','','','','','','')]
            tentativas = 0
            while True:
                # Rola mais a página
                #chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                for x in range(3):
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(1)
                
                posicao_atual = chrome_driver.execute_script("return window.pageYOffset;")
                if posicao_final == posicao_atual:
                    tentativas += 1
                    # A rolagem terminou 
                    if tentativas >= 3:
                        rolagem = False
                        break
                    else:
                        time.sleep(2) # Espera um pouco antes de rolar novamente
                else:
                    posicao_final = posicao_atual
                    break
        # Salva os tweets 
        with open('tweets/'+mes+'/'+usuario+de+'ate'+ate+'.csv','w',newline='', encoding='utf-8') as f:
            header = ['nome','usuario','idTweet','dataPublicacao','texto','replies','retweets','likes']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(dados)

        # A caixa de pesquisa passa a ser outro elemento (pois a página mudou)
        caixa_pesquisa = WebDriverWait(chrome_driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@data-testid="SearchBox_Search_Input"]'))
        )
        time.sleep(1)

parser = argumentos()
args = parser.parse_args()

# Coloca os usuarios do twitter dos deputados em um array
dados_deputados = csv.reader(open('deputados.csv'), delimiter=",", quotechar='|')
deputados = [row[5] for row in dados_deputados]
del deputados[0]

#Para nao repetir tweets ja coletados
files = []
for file in glob.glob("tweets/"+args.mes+"/*.csv"):
    files.append(file.split('2023')[0])
files = [x.split('/')[-1].replace('.csv','') for x in files]

usuarios = []
for x in deputados:
    if(x.split('/')[-1] not in files):
        usuarios.append(x)
print(len(usuarios), 'usuários não coletados')


chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("detach", True)

chrome_driver = webdriver.Chrome(options=chrome_options)

#   Abre o Chrome
chrome_driver.maximize_window()

#   Realiza Login
realizaLogin(args.user, args.email, args.password, chrome_driver)

#   Busca tweets dos usuarios listados
buscaTweets(usuarios, args.mes, chrome_driver)

#   Fecha o Chrome
chrome_driver.close()

