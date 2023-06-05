from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from argparse import ArgumentParser
from getpass import getpass
import time 
import csv
import glob
import math

def get_args(parser = ArgumentParser()):
    parser.add_argument( "-user", "--user", type = str, help = "Usuário do twitter")
    parser.add_argument( "-password", "--password", type = str, help = "Senha do twitter")
    parser.add_argument( "-mes", "--mes", type=str, help = "Mês de coleta das replies dos tweets no ano de 2023")
    parser.add_argument( "-email", "--email", type = str, help = "Email da conta do twitter (caso seja necessário autenticação)")
    parser.add_argument( "-chunk", "--chunk", type = int, help = "O chunk que será coletado (considerando chunks de 500 linhas)")
    return parser

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

def get_dados_tweet(tweet, tweetPai):
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
    
    dados = (nome,usuario,idTweet,dataPublicacao,texto,replies,retweets,likes,tweetPai)
    return dados

def coleta_replies(tweets, mes, chrome_driver):
    i=1
    for link in tweets:
        print(i, 'de', len(tweets))
        print(link)
        chrome_driver.get(link)
        body = WebDriverWait(chrome_driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body')))      
        dados = []
        tweet_ids = set()
        posicao_final = chrome_driver.execute_script("return window.pageYOffset;")
        rolagem = True

        while rolagem:
            #Tenta mostrar mais respostas
            try:
                mais_respostas_button = WebDriverWait(chrome_driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Mostrar mais respostas")]'))
                )
                chrome_driver.execute_script("arguments[0].click();", mais_respostas_button)
                time.sleep(1)
            except:
                pass
            #Tenta mostrar respostas ocultas
            try:
                mostrar_button = WebDriverWait(chrome_driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[normalize-space(text())='Mostrar']"))
                )
                chrome_driver.execute_script("arguments[0].click();", mostrar_button)
                time.sleep(1)
            except:
                pass

            # Procura replies
            try:
                if WebDriverWait(chrome_driver, 10).until(EC.presence_of_element_located((By.XPATH, '//article[@data-testid="tweet"]'))):
                    replies = chrome_driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
            except:
                replies = []
            if len(replies) > 1:
                for reply in replies:
                    dados_reply = get_dados_tweet(reply, link)
                    if dados_reply:
                        tweet_id = dados_reply[2]
                        if tweet_id not in tweet_ids and tweet_id != link:
                            tweet_ids.add(tweet_id)
                            dados.append(dados_reply)
            else:
                # Nenhuma replie encontrada
                dados = [('','','','','','','','',link)]
                break
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
        # saving the tweet 
        with open('replies/'+mes+'/'+link.split('/')[-1]+'.csv','w',newline='', encoding='utf-8') as f:
            header = ['nome','usuario','idTweet','dataPublicacao','texto','replies','retweets','likes','tweetPai']
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(dados)
        i=i+1

parser = get_args()
args = parser.parse_args()

mes = args.mes
data = csv.reader(open('tweets/'+mes+'/all.csv',  encoding="utf8"), delimiter=",", quotechar='"')
links = []
for linha in data:
    #Adiciona somente tweets com comentários
    if(linha[2]) and linha[5] > '0.0':
        links.append(linha[2])
del links[0]

print('Quantidade total de replies:',len(links))
#Quebra o vetor em 20 chunks
print('Quantidade total de chunks:',20)
n = math.ceil(len(links)/20)
print('Quantidade maxima por chunk:',n)
l = [links[i:i + n] for i in range(0, len(links), n)]

#Para nao repetir dados ja coletados
files = []
for file in glob.glob("replies/"+mes+"/*.csv"):
    files.append(file)
files = [x.split('/')[-1].replace('.csv','') for x in files]

tweets = []
for x in l[args.chunk]:
    if(x.split('/')[-1] not in files and len(x)>1):
        tweets.append(x)

chrome_options = Options()
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option("detach", True)

# setting the options & going to website 
chrome_driver = webdriver.Chrome(options=chrome_options)

# open the browser and maximize the window
chrome_driver.maximize_window()

realizaLogin(args.user, args.email, args.password, chrome_driver)
time.sleep(3)
coleta_replies(tweets, mes, chrome_driver)

chrome_driver.close()
