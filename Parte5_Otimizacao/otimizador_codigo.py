#########################################################################################################################################
### CÓDIGO OTIMIZADOR DA AST - LINGUAGEM <SHODAN>                                                                                     ###
#########################################################################################################################################

from copy import deepcopy


# FUNÇÃO PRINCIPAL - OTIMIZADOR DA AST
#########################################################################################################################################
# Recebe como entrada a Abstract Syntax Tree produzida pelo módulo da AST
def otimizar_ast(ast):
    # Variável de controle para detectar se a otimização está fazendo mudanças
    mudou = True

    # Enquanto estiverem sendo feitas modificações na árvore através da otimização, continua
    while mudou:
        mudou = False

        # As otimizações realizadas são:
        # Propagação de constantes
        mudou |= propagacao_constantes(ast)
        # Folding de constantes
        mudou |= folding_constantes(ast)

    # Ao final, retorna a AST otimizada
    return ast

# FUNÇÃO DE OTIMIZAÇÃO 1 - Propagação de constantes
def propagacao_constantes(ast):
    # Inicia um dicionário vazio que vai salvando as variáveis com constantes,
    # conforme elas vão sendo continuamente propagadas pelo programa
    constantes = {}

    # A propagação e feita por todo o código do programa
    mudou = propagar_programa(ast, constantes)

    # Ao final, ela retorna se houve alguma propagação (TRUE) ou nada se propagou (FALSE)
    return mudou

# Função para propagar para o código, isto é, para um conjunto de instruções
def propagar_programa(no, constantes):
    mudou = False

    # Para tal, é executada a propagação para cada uma das instruções do programa
    for instrucao in no.filhos:
        mudou |= propagar_instrucao(instrucao, constantes)

    return mudou

# Função para propagar as constantes individualmente por cada subárvore de instrução
# Executando diferentemente a depender do tipo de instrução
def propagar_instrucao(no, constantes):
    mudou = False

    # Subárvore de instrução de "DECLARAÇÃO"
    if no.categoria == "DECLARACAO":
        mudou |= propagar_declaracao(no, constantes)

    # Subárvore de instrução de "ATRIBUIÇÃO"
    elif no.categoria == "ATRIBUICAO":
        mudou |= propagar_atribuicao(no, constantes)

    # Subárvore de instrução de IMPRESSÃO "PRINT"
    elif no.categoria == "PRINT":
        mudou |= propagar_print(no, constantes)

    # Subárvore de instrução de LAÇO "WHILE"
    elif no.categoria == "WHILE":
        mudou |= propagar_while(no, constantes)

    # Subárvore de instrução de CADEIA IF-ELSEIF-ELSE
    elif no.categoria == "IF_ELSE":
        mudou |= propagar_ifelse(no, constantes)

    return mudou

# Para propagar constantes em uma "DECLARAÇÃO"
def propagar_declaracao(no, constantes):
    # Primeiro, obtém-se o nó da variável em si declarada
    id_no = no.filhos[1]
    # E a subárvore da expressão (valor) com o qual ela está sendo declarada
    expr_no = no.filhos[2]

    # Então, obtém-se o nome da variável
    nome_variavel = id_no.valor

    # Então, tenta-se propagar para dentro de sua expressão de declaração
    mudou = propagar_expressao(expr_no, constantes)

    # Se a expressão for um literal (INT, FLOAT, ou STRING)
    if eh_literal(expr_no):
        # Então salva qual o valor da variável atualmente declarada
        constantes[nome_variavel] = deepcopy(expr_no)
        # A fim de propagar o valor dela adiante

    # Se a expressão não é um literal
    else:
        # Então remove a variável do conjunto de constantes
        constantes.pop(nome_variavel, None)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para propagar constantes em uma "ATRIBUIÇÃO"
def propagar_atribuicao(no, constantes):
    # Primeiro, obtém-se o nó da variável em si declarada
    id_no = no.filhos[0]
    # E a subárvore da expressão (valor) que está sendo atribuída a ela
    expr_no = no.filhos[1]

    # Então, obtém-se o nome da variável
    nome_variavel = id_no.valor

    # Então, tenta-se propagar para dentro de sua expressão de atribuição
    mudou = propagar_expressao(expr_no, constantes)

    # Se a expressão for um literal (INT, FLOAT, ou STRING)
    if eh_literal(expr_no):
        # Então salva qual o valor da variável atribuída atualmente
        constantes[nome_variavel] = deepcopy(expr_no)
        # A fim de propagar o valor dela adiante

    # Se a expressão não é um literal
    else:
        # Então remove a variável do conjunto de constantes
        constantes.pop(nome_variavel, None)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para propagar constantes em uma IMPRESSÃO "PRINT"
def propagar_print(no, constantes):
    # Primeiro obtém-se a subárvore da expressão (valor) que está sendo imprimida
    expr_no = no.filhos[0]

    # Então, tenta-se propagar para dentro da expressão imprimida
    mudou = propagar_expressao(expr_no, constantes)
    
    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para propagar constantes em um LAÇO "WHILE"
def propagar_while(no, constantes):
    # Aqui, há um detalhe a se notar: um WHILE é uma quebra de fluxo,
    # então ele não segue a mesma lógica de propagação,
    # caso contrário ele propagaria constantes indevidamente 
    
    mudou = False

    # Primeiramente, assim que um WHILE quebra o fluxo,
    # todas as constantes propagadas até então serão esquecidas
    # (pois não há mais certeza de seu valor a partir daqui)
    constantes.clear()
    # (Não se propaga nada para dentro da CONDIÇÃO!)

    # Entretanto, ainda é possível realizar propagações locais dentro do BLOCO do WHILE
    # Então, para isso, obtém-se a subárvere do BLOCO
    bloco = no.filhos[1]

    # Então, tenta-se propagar as constantes dentro do bloco
    mudou |= propagar_bloco(bloco, constantes)

    # E, ao final, é necessário esquecer novamente todas as constantes que foram propagadas localmente,
    # para elas não vazarem e contaminarem o resto do código com informações potencialmente erradas
    constantes.clear()

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para propagar constantes em uma CADEIA "IF-ELSEIF-ELSE"
def propagar_ifelse(no, constantes):
    # Aqui, há um detalhe a se notar: um IF-ELSE é uma quebra de fluxo,
    # então ele não segue a mesma lógica de propagação,
    # caso contrário ele propagaria constantes indevidamente 
    
    mudou = False

    # Primeiramente, assim que um IF-ELSE quebra o fluxo,
    # todas as constantes propagadas até então serão esquecidas
    # (pois não há mais certeza de seu valor a partir daqui)
    constantes.clear()
    # (Não se propaga nada para dentro da CONDIÇÃO!)

    # Entretanto, ainda é possível realizar propagações locais dentro doS BLOCOs

    # Para isso, tenta-se propagar localmente dentro de cada subárvore
    for filho in no.filhos:
        # Propagar dentro do filho IF
        if filho.categoria == "IF":
            mudou |= propagar_if(filho, constantes)
        
        # Propagar dentro do(s) filho(s) ELSEIF
        elif filho.categoria == "ELSEIF":
            mudou |= propagar_elseif(filho, constantes)

        # Propagar dentro do filho ELSE
        elif filho.categoria == "ELSE":
            mudou |= propagar_else(filho, constantes)

        # E, ao final, após a propagação interna de cada filho,
        # é necessário esquecer novamente todas as constantes que foram propagadas localmente,
        # para elas não vazarem e contaminarem os outros filhos (entre IF, ELSEIFs e ELSE)
        constantes.clear()
    # E também para não vazar para o resto do código

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para propagar dentro de um "IF"
def propagar_if(no, constantes):
    # Obtém-se a subárvere do BLOCO
    bloco = no.filhos[1]

    # Então, tenta-se propagar as constantes dentro do bloco
    # E retorna se conseguiu ou não fazer alguma otimização
    return propagar_bloco(bloco, constantes)

# Para propagar dentro de um "ELSEIF"
def propagar_elseif(no, constantes):
    # Obtém-se a subárvere do BLOCO
    bloco = no.filhos[1]

    # Então, tenta-se propagar as constantes dentro do bloco
    # E retorna se conseguiu ou não fazer alguma otimização
    return propagar_bloco(bloco, constantes)

# Para propagar dentro de um "ELSE"
def propagar_else(no, constantes):
    # Obtém-se a subárvere do BLOCO
    bloco = no.filhos[0]

    # Então, tenta-se propagar as constantes dentro do bloco
    # E retorna se conseguiu ou não fazer alguma otimização
    return propagar_bloco(bloco, constantes)

# Então, para propagar as constantes dentro de um bloco, seja de WHILE, IF, ELSEIF ou ELSE
def propagar_bloco(no, constantes):
    # Propaga-se as constantes dentro de todas as instruções dentro dele
    return propagar_programa(no, constantes)

# Finalmente, para propagar uma expressão de fato
def propagar_expressao(no, constantes):
    mudou = False

    # Se encontrar uma variável
    if no.categoria == "ID":
        # Cujo valor seja constante
        if no.valor in constantes:
            # Salva o valor constante conhecido
            literal = constantes[no.valor]

            # E propaga a categoria
            no.categoria = literal.categoria
            # E principalmente o valor para a expressão
            no.valor = literal.valor
            # E elimina seus filhos (agora é constante)
            no.filhos = []

            return True

    # Fazendo isso para todos os níveis hierárquicos da expressão
    for filho in no.filhos:
        mudou |= propagar_expressao(filho, constantes)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou


# FUNÇÃO DE OTIMIZAÇÃO 2 - Folding de constantes
def folding_constantes(ast):
    # A propagação e feita por todo o código do programa
    # Retornando se houve algum folding (TRUE) ou nenhum folding (FALSE)
    return folding_programa(ast)

# Função para executar folding no código, isto é, para um conjunto de instruções
def folding_programa(no):
    mudou = False

    # Para tal, é executado o folding para cada uma das instruções do programa
    for instrucao in no.filhos:
        mudou |= folding_instrucao(instrucao)

    return mudou

# Função para executar folding das constantes individualmente por cada subárvore de instrução
# Executando diferentemente a depender do tipo de instrução
def folding_instrucao(no):
    mudou = False

    # Subárvore de instrução de "DECLARAÇÃO"
    if no.categoria == "DECLARACAO":
        mudou |= folding_declaracao(no)

    # Subárvore de instrução de "ATRIBUIÇÃO"
    elif no.categoria == "ATRIBUICAO":
        mudou |= folding_atribuicao(no)

    # Subárvore de instrução de IMPRESSÃO "PRINT"
    elif no.categoria == "PRINT":
        mudou |= folding_print(no)

    # Subárvore de instrução de LAÇO "WHILE"
    elif no.categoria == "WHILE":
        mudou |= folding_while(no)

    # Subárvore de instrução de CADEIA IF-ELSEIF-ELSE
    elif no.categoria == "IF_ELSE":
        mudou |= folding_ifelse(no)

    return mudou

# Para executar folding de constantes em uma "DECLARAÇÃO"
def folding_declaracao(no):
    # Primeiro, obtém-se a subárvore da expressão (valor) com o qual ela está sendo declarada
    expr = no.filhos[2]

    # Então, tenta-se executar folding na expressão de declaração
    # E retorna se conseguiu ou não fazer alguma otimização
    return folding_expressao(expr)

# Para executar folding de constantes em uma "ATRIBUIÇÃO"
def folding_atribuicao(no):
    # Primeiro, obtém-se a subárvore da expressão (valor) que está sendo atribuída
    expr = no.filhos[1]

    # Então, tenta-se executar folding na expressão de atribuição
    # E retorna se conseguiu ou não fazer alguma otimização
    return folding_expressao(expr)

# Para executar folding de constantes em uma IMPRESSÃO "PRINT"
def folding_print(no):
    # Primeiro obtém-se a subárvore da expressão (valor) que está sendo imprimida
    expr = no.filhos[0]
    # Observação: no momento atual, 'print' não aceita expressões, então nunca haverá folding
    # Porém, optou-se deixar aqui a função para fins didáticos e possíveis reaproveitamentos

    # E retorna que não conseguiu fazer nenhuma otimização
    return folding_expressao(expr)

# Para executar folding de constantes em um LAÇO "WHILE"
def folding_while(no):
    mudou = False

    # Primeiramente, obtém-se a subárvere da CONDIÇÃO
    condicao = no.filhos[0]
    # E a subárvere do BLOCO
    bloco = no.filhos[1]

    # Então, tenta-se executar folding dentro da condição
    mudou |= folding_expressao(condicao.filhos[0])

    # E tenta-se executar folding dentro do bloco
    mudou |= folding_bloco(bloco)

    return mudou

# Para executar folding de constantes em uma CADEIA "IF-ELSEIF-ELSE"
def folding_ifelse(no):
    mudou = False

    # Tenta-se executar folding dentro de cada subárvore
    for filho in no.filhos:
        # Executar folding dentro do filho IF
        if filho.categoria == "IF":
            mudou |= folding_if(filho)

        # Executar folding dentro do filho ELSEIF
        elif filho.categoria == "ELSEIF":
            mudou |= folding_elseif(filho)

        # Executar folding dentro do filho ELSE
        elif filho.categoria == "ELSE":
            mudou |= folding_else(filho)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para executar folding dentro de um "IF"
def folding_if(no):
    # Obtém-se a subárvere da CONDIÇÃO
    condicao = no.filhos[0]
    # E a subárvere do BLOCO
    bloco = no.filhos[1]

    mudou = False

    # Então, tenta-se executar folding das constantes dentro da condição
    mudou |= folding_expressao(condicao.filhos[0])
    # E tenta-se executar folding das constantes dentro do bloco
    mudou |= folding_bloco(bloco)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para executar folding dentro de um "ELSEIF"
def folding_elseif(no):
    # Obtém-se a subárvere da CONDIÇÃO
    condicao = no.filhos[0]
    # E a subárvere do BLOCO
    bloco = no.filhos[1]

    mudou = False

    # Então, tenta-se executar folding das constantes dentro da condição
    mudou |= folding_expressao(condicao.filhos[0])
    # E tenta-se executar folding das constantes dentro do bloco
    mudou |= folding_bloco(bloco)

    # E retorna se conseguiu ou não fazer alguma otimização
    return mudou

# Para executar folding dentro de um "ELSE"
def folding_else(no):
    # Obtém-se a subárvere do BLOCO
    bloco = no.filhos[0]

    # Então, tenta-se executar folding das constantes dentro do bloco
    # E retorna se conseguiu ou não fazer alguma otimização
    return folding_bloco(bloco)

# Então, para executar folding das constantes dentro de um bloco, seja de WHILE, IF, ELSEIF ou ELSE
def folding_bloco(no):
    # Executa-se folding das constantes dentro de todas as instruções dentro dele
    return folding_programa(no)

# Finalmente, para executar folding de uma expressão de fato
def folding_expressao(no):
    mudou = False

    # Primeiramente, o folding é executado dos filhos primeiro (bottom-up)
    # Da hierarquia das folhas para a raiz
    for filho in no.filhos:
        # Tentando fazer folding para cada um dos filhos
        mudou |= folding_expressao(filho)

    # Folding de operações matemáticas:
    if no.categoria in ("NUMOP_+-", "NUMOP_*/", "NUMOP_^"):
        # Obtendo os operandos esquerdo e direito
        esq = no.filhos[0]
        dir = no.filhos[1]

        # Se ambos os operandos forem literais numéricos (INT ou FLOAT)
        if (esq.categoria in ("INT", "FLOAT") and dir.categoria in ("INT", "FLOAT")):
            # Obtém os valor numéricos deles
            valor_esq = esq.valor
            valor_dir = dir.valor

            # E realiza a operação matemática diretamente:
            # Operação de soma
            if no.valor == "+":
                resultado = valor_esq + valor_dir
            # Operação de subtração
            elif no.valor == "-":
                resultado = valor_esq - valor_dir
            # Operação de multiplicação
            elif no.valor == "*":
                resultado = valor_esq * valor_dir
            # Operação de divisão
            elif no.valor == "/":
                try:
                    resultado = valor_esq / valor_dir
                # Observação importante: Caso um erro de DIVISÃO POR ZERO ocorra durante o folding
                except ZeroDivisionError:
                    # Esse erro é comunicado à main
                    raise Exception(
                        f"\n-----------------------------------------------------------------------\n"
                        "ERRO DE EXECUCAO:\n"
                        "Divisao por zero."
                    )
            # Operação de potenciação
            elif no.valor == "^":
                try:
                    resultado = valor_esq ** valor_dir
                # Observação importante: Caso um erro de OVERFLOW ocorra durante o folding
                except OverflowError:
                    # Esse erro é comunicado à main
                    raise Exception(
                        "\n-----------------------------------------------------------------------\n"
                        "ERRO DE EXECUCAO:\n"
                        "Numero muito grande para representacao."
                    )
            
            # Observação importante: Caso um erro de INTEIRO COM NÚMERO DE DÍGITOS MUITO GRANDE ocorra durante o folding
            if isinstance(resultado, int):
                if resultado.bit_length() > 4096:
                    # Esse erro é comunicado à main
                    raise Exception(
                        f"\n-----------------------------------------------------------------------\n"
                        "ERRO DE EXECUCAO:\n"
                        "Overflow numerico."
                    )

            # Assim, o resultado do folding da operação numérica é salvo, a depender se resultou num FLOAT ou em um INT
            if isinstance(resultado, float):
                no.categoria = "FLOAT"
            else:
                no.categoria = "INT"

            # Salvando o resultado
            no.valor = resultado
            # E eliminando os filhos
            no.filhos = []

            # E retornando que houve uma otimização
            return True

    # Folding de operações relacionais:
    if no.categoria == "RELOP":
        # Obtendo os operandos esquerdo e direito
        esq = no.filhos[0]
        dir = no.filhos[1]

        # Se ambos os operandos forem literais numéricos (INT ou FLOAT)
        if (esq.categoria in ("INT", "FLOAT") and dir.categoria in ("INT", "FLOAT")):
            # Obtém os valor numéricos deles
            valor_esq = esq.valor
            valor_dir = dir.valor

            # E realiza a operação relacional diretamente:
            # Operação de comparação de igual
            if no.valor == "==":
                resultado = valor_esq == valor_dir
            # Operação de comparação de diferente
            elif no.valor == "!=":
                resultado = valor_esq != valor_dir
            # Operação de comparação de maior
            elif no.valor == ">":
                resultado = valor_esq > valor_dir
            # Operação de comparação de menor
            elif no.valor == "<":
                resultado = valor_esq < valor_dir
            # Operação de comparação de maior ou igual
            elif no.valor == ">=":
                resultado = valor_esq >= valor_dir
            # Operação de comparação de menor ou igual
            elif no.valor == "<=":
                resultado = valor_esq <= valor_dir

            # Assim, o resultado do folding da operação relacional é salvo, como um BOOLEANO
            no.categoria = "BOOL"
            
            # Salvando o resultado
            no.valor = resultado
            # E eliminando os filhos
            no.filhos = []

            # E retornando que houve uma otimização
            return True

        # Se ambos os operandos forem literais STRINGs
        if (esq.categoria == "STRING" and dir.categoria == "STRING"):
            # Realiza a operação relacional diretamente:
            # Operação de comparação de igual
            if no.valor == "==":
                resultado = esq.valor == dir.valor
            # Operação de comparação de diferente
            elif no.valor == "!=":
                resultado = esq.valor != dir.valor

            else:
                return mudou

            # Assim, o resultado do folding da operação relacional é salvo, como um BOOLEANO
            no.categoria = "BOOL"

            # Salvando o resultado
            no.valor = resultado
            # E eliminando os filhos
            no.filhos = []

            # E retornando que houve uma otimização
            return True

    # Folding de operações lógicas: AND
    if no.categoria == "LOGIC_AND":
        # Obtendo os operandos esquerdo e direito
        esq = no.filhos[0]
        dir = no.filhos[1]

        # Se ambos os operandos forem BOOLEANOS
        if (esq.categoria == "BOOL" and dir.categoria == "BOOL"):
            # Salva-se o resultado da operação AND, como um BOOLEANO
            no.categoria = "BOOL"
            # E realiza a operação AND diretamente:
            no.valor = esq.valor and dir.valor
            # E elimina os filhos
            no.filhos = []

            # E retorna que houve uma otimização
            return True

    # Folding de operações lógicas: OR
    if no.categoria == "LOGIC_OR":
        # Obtendo os operandos esquerdo e direito
        esq = no.filhos[0]
        dir = no.filhos[1]

        # Se ambos os operandos forem BOOLEANOS
        if (esq.categoria == "BOOL" and dir.categoria == "BOOL"):
            # Salva-se o resultado da operação OR, como um BOOLEANO
            no.categoria = "BOOL"
            # E realiza a operação OR diretamente:
            no.valor = esq.valor or dir.valor
            # E elimina os filhos
            no.filhos = []

            # E retorna que houve uma otimização
            return True

    # Folding de operações lógicas: NOT
    if no.categoria == "LOGIC_NOT":
        # Obtendo o operando a ser negado
        operando = no.filhos[0]

        # Se o operando for BOOLEANO
        if operando.categoria == "BOOL":
            # Salva-se o resultado da operação NOT, como um BOOLEANO
            no.categoria = "BOOL"
            # E realiza a operação NOT diretamente:
            no.valor = not operando.valor
            # E elimina os filhos
            no.filhos = []

            # E retorna que houve uma otimização
            return True

    # Folding de operações unárias: +
    if no.categoria == "UNARIO_+":
        # Obtendo o operando
        operando = no.filhos[0]

        # Se o operando for literal numérico (INT ou FLOAT)
        if operando.categoria in ("INT", "FLOAT"):
            # Salva-se o resultado da operação + UNÁRIO
            no.categoria = operando.categoria
            # E realiza a operação + UNÁRIA diretamente:
            no.valor = +operando.valor
            # E elimina os filhos
            no.filhos = []

            # E retorna que houve uma otimização
            return True

    # Folding de operações unárias: +
    if no.categoria == "UNARIO_-":
        # Obtendo o operando
        operando = no.filhos[0]

        # Se o operando for literal numérico (INT ou FLOAT)
        if operando.categoria in ("INT", "FLOAT"):
            # Salva-se o resultado da operação + UNÁRIO
            no.categoria = operando.categoria
            # E realiza a operação + UNÁRIA diretamente:
            no.valor = -operando.valor
            # E elimina os filhos
            no.filhos = []

            # E retorna que houve uma otimização
            return True

    # Ao final, retorna se houve ou não alguma otimização
    return mudou

# Função auxiliar para verificar se um nó trata-se de um literal
def eh_literal(no):
    return no.categoria in ("INT", "FLOAT", "STRING", "BOOL")