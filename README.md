
# Monografia I - Scripts utilizados

Este repositório engloba os principais scripts utilizados durante a Monografia I, sobretudo referente a coleta de dados.

## ListagemDeputadosComTwitter.ipynb
O notebook lista todos os deputados que estiveram em exercício desde 1 de janeiro de 2023 até o período atual (ultima execução: 4 de junho), e gera o arquivo `deputados.csv` com os dados coletados.

## tweetScraper.py
Coleta todos os tweets dos deputados listados no arquivo `deputados.csv`. Para rodar basta utilizar as informações de login de uma conta do Twitter e informar o mês de coleta desejado (entre janeiro e maio):

`python tweetScraper.py -user usuariotwitter -password senhatwitter -email emailtwitter -mes mesdesejado`

## replieScraper.py
Coleta todas as replies de cada tweet listado de cada mês. Para rodar, além de informar as informações de login e o mês de coleta desejado, é preciso informar o `chunk` a ser coletado (um número inteiro de 0 a 19).

`python replyScraper.py -user usuariotwitter -password senhatwitter -email emailtwitter -chunk chunkdesejado -mes mesdesejado`

## validador.py
O script itera por cada tweet coletado e verifica se as replies de cada um foram coletadas.
