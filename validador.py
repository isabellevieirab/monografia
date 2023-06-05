import os
import pandas as pd 
import glob
import time 
import csv

# Coloca os usuarios do twitter dos deputados em um array
dados_deputados = csv.reader(open('deputados.csv'), delimiter=",", quotechar='|')
deputados = [row[5] for row in dados_deputados]
del deputados[0]


# Para cada mês, vê se todas as replies de todos os tweets foram coletados
meses = ['janeiro','fevereiro', 'marco', 'abril','maio']
ausentes = []

for mes in meses:
    data = csv.reader(open('tweets/'+mes+'/all.csv',  encoding="utf8"), delimiter=",", quotechar='"')
    
    # Array dos tweets a serem coletados
    links = []
    for linha in data:
        #Adiciona somente tweets com comentários
        if(linha[2]) and linha[5] > '0.0':
            links.append(linha[2])
    del links[0]

    # Array dos tweets já salvos
    files = []
    for file in glob.glob("replies/"+mes+"/*.csv"):
        files.append(file)
    files = [x.split('/')[-1].replace('.csv','') for x in files]

    # Adiciona os tweets que ainda não foram coletados
    for x in links:
        if(x.split('/')[-1] not in files and len(x)>1):
            ausentes.append((mes,x))

if(len(ausentes)>0):
    print(len(ausentes),'tweets não coletados:')
    for i in ausentes:
        print(i)
else:
    print('Ok')

