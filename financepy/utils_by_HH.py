# Funcoes uteis para o projeto
# Autor: Hernan Lobert
# Data: 2023-10-02

"""import the packages that we'll use"""

# time
import datetime as dt

# excel wrapper
import xlwings as xw

# plot
import matplotlib.pyplot as plt

# Data wrappers
import pandas as pd
import numpy as np

""" Funcoes de debug """


def print_debug(nome_aba: str, linha: int, texto: str, verbal: bool = True) -> int:
    """Imprime o texto na aba e linha passadas (sempre na primeira coluna = A:A). 
    Retorna linha+1."""
    # verifica se eh para escrever a mensagem
    if verbal:
        # Clear output se for a primeira linha
        if linha == 1:
            xw.Book.caller().sheets[nome_aba].range("A:A").clear_contents()
        # escreve a informacao
        xw.Book.caller().sheets[nome_aba].range("A" + str(linha)).value = (
            dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + " - " + texto
        )
        # aumenta uma linha se escreveu alguma coisa
        return linha + 1
    else:
        # Se nao for para escrever nada, apenas retorna a linha atual
        return linha


def teste_de_conexao():
    """Faz um teste de conexao e imprime no excel uns valores aleatorios."""
    # import especifico
    import random

    # nome da aba Debug e inicializa a linha de debug
    aba_debug = "debug"
    linha_debug = print_debug(aba_debug, 1, "### Iniciando teste de conexao ###")
    # mostra o nome da planilha chamando
    linha_debug = print_debug(aba_debug, linha_debug, f"Link do book: {xw.Book.caller()}")
    # mostra o nome da aba de 'debug'
    linha_debug = print_debug(
        aba_debug,
        linha_debug,
        f"Link da aba {aba_debug}: {xw.Book.caller().sheets[aba_debug]}",
    )
    # gera e escreve varios numeros aleatorios
    for x in range(10):
        linha_debug = print_debug(
            aba_debug,
            linha_debug + 1,
            f"    {x + 1} - Numero aleatorio: {random.uniform(1, 20):.0f}",
        )
    # coloca a data do teste
    linha_debug = print_debug(
        aba_debug,
        linha_debug + 1,
        f"Data do teste: {dt.date.today()} --- [ FULL DATE: {dt.datetime.now()}]",
    )
    # ajusta o formato do debug
    xw.Book.caller().sheets[aba_debug].range("A:A").wrap_text = False

    # nome
    aba_grafico_vol = "ResumoVol"
    linha_plot = 1
    # cria a variavel da planilha
    rc_book = xw.Book.caller()  # xw.Book(planilha)
    # cria a variavel da tab para o retorno das vol limpas e seu dados
    vol_grafico = rc_book.sheets[aba_grafico_vol]

    # cria grafico simples
    figura = plt.figure()
    plt.plot([1, 2, 3, 4, 5])

    # Coloca o grafico no excel
    nome = "Volatility-" + str(linha_plot)
    # posicao do grafico
    posicao = "A" + str(linha_plot)
    # vai na aba do grafico
    vol_grafico.select()
    vol_grafico.range(posicao).select()
    # Coloca o grafico no Excel
    plot = vol_grafico.pictures.add(
        # image=figura, name=nome, update=True, anchor=vol_grafico.range(posicao)
        image=figura,
        name=nome,
        update=True,
        # anchor=vol_grafico.range(posicao),
    )
    # Let's scale the plots
    plot.width, plot.height = 270, 190
    # plot.top = vol_grafico[posicao].top
    # plot.left = vol_grafico[posicao].left
    # fecha o grafico para poder criar um novo
    plt.close(figura)


""" Funcoes de graficos """


def print_texto(nome_aba, coluna, linha, texto):
    """Imprime o texto na aba e (linha, coluna) passadas. Retorna linha+1."""
    # escreve a informacao
    xw.Book.caller().sheets[nome_aba].range(coluna + str(linha)).value = texto
    # sheet_debug["A" + linha].value= texto
    return linha + 1


""" Funcoes de matematicas de estatisticas """


def media_ponderada(valor1, valor2, peso1, peso2):
    """Calcula a media ponderada de 2 valores com seus respectivos pesos."""
    # TODO: ir linha a linha veriricando os valor e fazendo a conta

    # checa se algum dos valores eh nulo
    if pd.isnull(valor1) or pd.isnull(valor2):
        return np.nan
    # verifica se os 2 pesos sao nulos. Nesse caso usa o mesmo peso
    if pd.isnull(peso1) and pd.isnull(peso2):
        peso1 = 1
        peso2 = 1
    # caso so o peso1 seja nulo usa o peso2
    elif pd.isnull(peso1):
        peso1 = peso2
    # caso so o peso1 seja nulo usa o peso2
    elif pd.isnull(peso2):
        peso2 = peso1
    # faz as contas
    temp = (valor1 * peso1) + (valor2 * peso2)
    temp = temp / (peso1 + peso2)
    # temp = np.average([valor1, valor2], weights=[peso1, peso2])
    return temp
