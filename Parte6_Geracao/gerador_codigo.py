#########################################################################################################################################
### CÓDIGO GERADOR DE CÓDIGO - LINGUAGEM <SHODAN>                                                                                     ###
#########################################################################################################################################

import math

# FUNÇÃO PRINCIPAL - GERADOR DE CÓDIGO PYTHON
#########################################################################################################################################
# Recebe como entrada a AST otimizada produzida pelo módulo do otimizador
def gerar_codigo(ast):
    # O gerador inicia criando uma lista vazia das linhas do código em python,
    # a ser preenchida com as linhas de instruções do código shodan
    linhas = []

    # Tabela dos tipos das variáveis, a ser usada posteriormente em uma atribuição
    tabela_tipos = {}
    # (Observação: é necessário salvar os tipos das variáveis declaradas pois python é uma linguagem que opera com tipagem dinâmica)

    # Gera o código python do usuário, traduzindo todo o programa 
    gerar_programa(ast, linhas, tabela_tipos)

    return "\n".join(linhas)

# Função que recebe o PROGRAMA e gera o código python a partir da AST otimizada
# Atualizando o nível de identação (com o qual o python trabalha) conforme necessário
def gerar_programa(no, linhas, tabela_tipos, nivel=0):
    for instrucao in no.filhos:
        gerar_instrucao(instrucao, linhas, tabela_tipos, nivel)

# Função que traduz e gera cada uma das instruções de shodan para python
def gerar_instrucao(no, linhas, tabela_tipos, nivel_indentacao):
    # Se for uma instrução de "DECLARAÇÃO"
    if no.categoria == "DECLARACAO":
        gerar_declaracao(no, linhas, tabela_tipos, nivel_indentacao)
    # Se for uma instrução de "ATRIBUIÇÃO"
    elif no.categoria == "ATRIBUICAO":
        gerar_atribuicao(no, linhas, tabela_tipos, nivel_indentacao)
    # Se for uma instrução de IMPRESSÃO "PRINT"
    elif no.categoria == "PRINT":
        gerar_print(no, linhas, nivel_indentacao)
    # Se for uma instrução de LAÇO "WHILE"
    elif no.categoria == "WHILE":
        gerar_while(no, linhas, tabela_tipos, nivel_indentacao)
    # Se for uma instrução de CADEIA "IF-ELSEIF-ELSE"
    elif no.categoria == "IF_ELSE":
        gerar_ifelse(no, linhas, tabela_tipos, nivel_indentacao)

# Para gerar uma declaração em python a partir de uma declaração em shodan
def gerar_declaracao(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó do tipo da variável,
    tipo_no = no.filhos[0]
    # O nó do nome da variável,
    id_no = no.filhos[1]
    # E o nó da expressão com a qual a variável está sendo declarada
    expr_no = no.filhos[2]

    # Obtendo o tipo e o nome propriamente ditos
    tipo = tipo_no.valor
    nome = id_no.valor
    # E atualizando a tabela com a informação do tipo da nova variável
    tabela_tipos[nome] = tipo

    # Gera o código da expressão em si
    expr = gerar_expressao(expr_no)

    # E faz um tratamento especial para tipos numéricos
    # Protegendo um INT de erros
    if tipo == "int":
        expr = f"shodan_int({expr})"
    # Protegendo um FLOAT de erros
    if tipo == "float":
        expr = f"shodan_float({expr})"

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # E criando a linha de código de uma declaração python
    linhas.append(f"{indentacao}{nome} = {expr}")

# Para gerar uma atribuição em python a partir de uma atribuição em shodan
def gerar_atribuicao(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó do nome da variável,
    id_no = no.filhos[0]
    # E o nó da expressão que está sendo atribuído à variável
    expr_no = no.filhos[1]

    # Obtendo o nome propriamente dito
    nome = id_no.valor
    # E consultando na tabela qual é o tipo com o qual ela foi declarada
    tipo = tabela_tipos[nome]

    # Gera o código da expressão em si
    expr = gerar_expressao(expr_no)
    
    # E faz um tratamento especial para tipos numéricos
    # Protegendo um INT de erros
    if tipo == "int":
        expr = f"shodan_int({expr})"
    # Protegendo um FLOAT de erros
    if tipo == "float":
        expr = f"shodan_float({expr})"

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # E criando a linha de código de uma atribuição python
    linhas.append(f"{indentacao}{nome} = {expr}")

# Para gerar um print em python a partir de um print em shodan
def gerar_print(no, linhas, nivel):
    # Primeiramente, obtém o nó da expressão que será impressa
    expr_no = no.filhos[0]

    # Gera o código da expressão em si
    expr = gerar_expressao(expr_no)

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # E criando a linha de código de um print python
    linhas.append(f"{indentacao}print({expr})")

# Para gerar um while em python a partir de um while em shodan
def gerar_while(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó da condição
    condicao_no = no.filhos[0]
    # E o nó do bloco
    bloco_no = no.filhos[1]

    # Gera o código da condição em si
    condicao = gerar_expressao(condicao_no)

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # Criando a linha de código de um while python
    linhas.append(f"{indentacao}while {condicao}:")

    # E, abaixo, gera o código do bloco em si, com uma identação extra
    gerar_bloco(bloco_no, linhas, tabela_tipos, nivel + 1)

# Para gerar um if-elif-else em python a partir de um if-elseif-else em shodan
def gerar_ifelse(no, linhas, tabela_tipos, nivel):
    # Gerando uma instrução python para cada condicional da cadeia
    for filho in no.filhos:
        if filho.categoria == "IF":
            gerar_if(filho, linhas, tabela_tipos, nivel)

        elif filho.categoria == "ELSEIF":
            gerar_elseif(filho, linhas, tabela_tipos, nivel)

        elif filho.categoria == "ELSE":
            gerar_else(filho, linhas, tabela_tipos, nivel)

# Para gerar um if em python a partir de um if em shodan
def gerar_if(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó da condição
    condicao_no = no.filhos[0]
    # E o nó do bloco
    bloco_no = no.filhos[1]

    # Gera o código da condição em si
    condicao = gerar_expressao(condicao_no)

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # Criando a linha de código de um if python
    linhas.append(f"{indentacao}if {condicao}:")

    # E, abaixo, gera o código do bloco em si, com uma identação extra
    gerar_bloco(bloco_no, linhas, tabela_tipos, nivel + 1)

# Para gerar um elif em python a partir de um elseif em shodan
def gerar_elseif(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó da condição
    condicao_no = no.filhos[0]
    # E o nó do bloco
    bloco_no = no.filhos[1]

    # Gera o código da condição em si
    condicao = gerar_expressao(condicao_no)

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # Criando a linha de código de um elif python
    linhas.append(f"{indentacao}elif {condicao}:")

    # E, abaixo, gera o código do bloco em si, com uma identação extra
    gerar_bloco(bloco_no, linhas, tabela_tipos, nivel + 1)

# Para gerar um else em python a partir de um else em shodan
def gerar_else(no, linhas, tabela_tipos, nivel):
    # Primeiramente, obtém o nó do bloco
    bloco_no = no.filhos[0]

    # Adicionando o nível de identação atual
    indentacao = "    " * nivel

    # Criando a linha de código de um else python
    linhas.append(f"{indentacao}else:")

    # E, abaixo, gera o código do bloco em si, com uma identação extra
    gerar_bloco(bloco_no, linhas, tabela_tipos, nivel + 1)

# E, para gerar o código do bloco python a partir de um bloco em shodan
def gerar_bloco(no, linhas, tabela_tipos, nivel):
    # Se o bloco for vazio
    if len(no.filhos) == 0:
        # Adicionando o nível de identação atual
        indentacao = "    " * nivel
        # Python requer que whiles,ifs,elifs e elses com blocos vazios tenham um pass
        linhas.append(f"{indentacao}pass")

        return

    # Senão, então gera o código python a partir da subárvore de código
    gerar_programa(no, linhas, tabela_tipos, nivel)

# Por fim, para gerar o código de uma expressão
# Recebe qualquer subárvore de expressão e devolve uma string python equivalente
def gerar_expressao(no):
    # Avaliando primeiro qual é a categoria (e, consequentemente, qual o tipo de expressão) do nó daquela subárvore
    categoria = no.categoria

    # Literais:
    # Se for apenas um INT
    if categoria == "INT":
        # Retorna apenas o valor inteiro dele
        return str(no.valor)
    # Se for apenas um FLOAT
    if categoria == "FLOAT":
        # Observação: caso haja a identificação de um 'inf' (valor muito alto, considerado "infinito") 
        if math.isinf(no.valor):
            # Gerará para a main um erro
            raise Exception(
                "ERRO DE EXECUCAO:\n"
                "Numero muito grande para representacao float."
            )
        # Observação: caso haja a identificação de um 'nan' (valor indefinido, considerado um "não número") 
        if math.isnan(no.valor):
            # Gerará para a main um erro
            raise Exception(
                "ERRO DE EXECUCAO:\n"
                "Valor numerico invalido."
            )
        # Se não houver problemas, retorna apenas o valor float dele
        return str(no.valor)

    # Se for apenas uma STRING
    if categoria == "STRING":
        # Retorna a própria string
        return repr(no.valor)

    # Se for apenas um BOOL
    if categoria == "BOOL":
        # Retorna o valor booleano dele
        return str(no.valor)


    # Se o nó for uma variável
    if categoria == "ID":
        # Retorna o valor armazenado nela
        return no.valor


    # Se o nó for uma condição:
    if categoria == "CONDICAO":
        # Retorna a avaliação booleana da condição em si (TRUE ou FALSE)
        return gerar_expressao(no.filhos[0])


    # Operadores numéricos:
    # Se o nó for uma soma, uma subtração, uma multiplicação ou uma divisão
    if categoria in ("NUMOP_+-", "NUMOP_*/"):
        # Obtém primeiro os valores dos operandos em si
        esq = gerar_expressao(no.filhos[0])
        dir = gerar_expressao(no.filhos[1])

        # Tratamento especial para divisão, a fim de evitar erros de divisão por zero
        if no.valor == "/":
            return f"shodan_div({esq}, {dir})"

        # Retorna a operação matemática em si
        return f"({esq} {no.valor} {dir})"

    # Se o nó for uma potenciação
    if categoria == "NUMOP_^":
        # Obtém primeiro os valores dos operandos em si
        esq = gerar_expressao(no.filhos[0])
        dir = gerar_expressao(no.filhos[1])

        # Tratamento especial para potenciação, a fim de evitar erros de overflow
        return f"shodan_pow({esq}, {dir})"


    # Operadores relacionais: se o operador for comparativo
    if categoria == "RELOP":
        # Obtém primeiro os valores dos operandos em si
        esq = gerar_expressao(no.filhos[0])
        dir = gerar_expressao(no.filhos[1])

        # Retorna a operação relacional em si
        return f"({esq} {no.valor} {dir})"


    # Operadores lógicos:
    # Se o nó for uma AND
    if categoria == "LOGIC_AND":
        # Obtém primeiro os valores dos operandos em si
        esq = gerar_expressao(no.filhos[0])
        dir = gerar_expressao(no.filhos[1])

        # Retorna a operação AND em si
        return f"({esq} and {dir})"

    # Se o nó for um OR
    if categoria == "LOGIC_OR":
        # Obtém primeiro os valores dos operandos em si
        esq = gerar_expressao(no.filhos[0])
        dir = gerar_expressao(no.filhos[1])

        # Retorna a operação OR em si
        return f"({esq} or {dir})"

    # Se o nó for um NOT
    if categoria == "LOGIC_NOT":
        # Obtém primeiro o valor do operando em si
        expr = gerar_expressao(no.filhos[0])

        # Retorna a operação NOT em si
        return f"(not {expr})"


    # Operadores unários:
    # Se o operador for um + Unário
    if categoria == "UNARIO_+":
        # Obtém primeiro o valor do operando em si
        expr = gerar_expressao(no.filhos[0])

        # Retorna a operação + unária em si
        return f"(+{expr})"


    # Se o operador for um - Unário
    if categoria == "UNARIO_-":
        # Obtém primeiro o valor do operando em si
        expr = gerar_expressao(no.filhos[0])

        # Retorna a operação - unária em si
        return f"(-{expr})"


    raise Exception(
        f"ERRO INTERNO:\n"
        f"Categoria desconhecida: "
        f"{categoria}"
    )