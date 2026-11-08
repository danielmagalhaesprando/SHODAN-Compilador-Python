#########################################################################################################################################
### CÓDIGO ANALISADOR SEMÂNTICO - LINGUAGEM <SHODAN>                                                                                  ###
#########################################################################################################################################

# FUNÇÃO PRINCIPAL - ANALISADOR SEMÂNTICO
#########################################################################################################################################
# Recebe como entrada a Abstract Syntax Tree produzida pelo módulo da AST
def analisar_semantica(ast):
    # Tabela de símbolos (variáveis) do código atual,
    # inicializada vazia e preenchida conforme o usuário declara novas variáveis
    tabela_simbolos = {}

    # Analisa o código do usuário como um todo, atualizando e verificando a tabela de símbolos,
    # e checando se a lógica semântica do programa está correta 
    analisar_programa(ast, tabela_simbolos)

    # Ao fim, retorna a tabela de símbolos do código
    return tabela_simbolos

# Função que recebe o PROGRAMA e analisa-o semanticamente, navegando pela AST
def analisar_programa(no, tabela):
    # Analisando cada uma das instruções contidas nele
    for filho in no.filhos:
        analisar_instrucao(filho, tabela)

# Função que analisa cada uma das instruções separadamente,
# decidindo a depender do tipo de instrução e encaminhando para cada analisador
def analisar_instrucao(no, tabela):
    # Se for uma "DECLARAÇÃO", analisa com base na lógica semântica de uma "DECLARAÇÃO"
    if no.categoria == "DECLARACAO":
        analisar_declaracao(no, tabela)

    # Se for uma "ATRIBUIÇÃO", analisa com base na lógica semântica de uma "ATRIBUIÇÃO"
    elif no.categoria == "ATRIBUICAO":
        analisar_atribuicao(no, tabela)

    # Se for uma IMPRESSÃO "PRINT", analisa com base na lógica semântica de um "PRINT"
    elif no.categoria == "PRINT":
        analisar_print(no, tabela)

    # Se for um LAÇO "WHILE", analisa com base na lógica semântica de um "WHILE"
    elif no.categoria == "WHILE":
        analisar_while(no, tabela)

    # Se for uma CADEIA "IF-ELSE", analisa com base na lógica semântica de um "IF-ELSE"
    elif no.categoria == "IF_ELSE":
        analisar_ifelse(no, tabela)

# Função que analisa uma subárvore de instrução de DECLARAÇÃO
def analisar_declaracao(no, tabela):
    # Obtendo da subárvore:
    # o nó do tipo da variável declarada
    tipo_no = no.filhos[0]
    # o nó do nome da variável sendo declarada
    id_no = no.filhos[1]
    # o nó do valor com a qual a variável está sendo declarada
    expr_no = no.filhos[2]

    # Extraindo o tipo e o nome propriamente ditos
    tipo_variavel = tipo_no.valor
    nome_variavel = id_no.valor
    # Inferindo o tipo da expressão em si
    tipo_expr = inferir_tipo(expr_no, tabela)

    # I - Primeira verificação: variável já foi declarada antes?
    # Se sim (isto é, seu nome consta na tabela de variáveis já declaradas)
    if nome_variavel in tabela:
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {id_no.linha}, "
            f"Coluna {id_no.coluna}\n\n"
            f"Variavel '{nome_variavel}' ja declarada,\n"
            f"na linha {tabela[nome_variavel]['linha']} coluna {tabela[nome_variavel]['coluna']}."
        )

    # II - Segunda verificação: tipo com o qual a variável foi declarada é compatível com o valor com o qual ela foi declarada?
    # Se não (isto é, o tipo da variável e da expressão não são compatíveis)
    if not tipos_compativeis(tipo_variavel, tipo_expr):
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr_no.linha}, "
            f"Coluna {expr_no.coluna}\n\n"
            f"Nao e possivel declarar a variavel '{nome_variavel}', do tipo '{tipo_variavel}',\n"
            f"com valor da expressao do tipo '{tipo_expr}'."
        )

    # Caso não haja nenhum problema semântico, então, declarou-se com sucesso uma nova variável
    # A qual é salva na tabela de variáveis
    tabela[nome_variavel] = {
        "tipo": tipo_variavel,  # Salvando o seu tipo
        "linha": id_no.linha,   # A linha onde ela começa
        "coluna": id_no.coluna  # E a coluna onde ela começa
    }
                                # (Obs.: não precisa salvar o valor da expressão, pois o semântico não avalia isso em momento nenhum)

# Função que analisa uma subárvore de instrução de ATRIBUIÇÃO
def analisar_atribuicao(no, tabela):
    # Obtendo da subárvore:
    # o nó do nome da variável que está sendo reatribuída
    id_no = no.filhos[0]
    # o nó do valor que está sendo atribuído à variável
    expr_no = no.filhos[1]

    # Extraindo o o nome propriamente dito
    nome_variavel = id_no.valor

    # I - Primeira verificação: variável já foi declarada antes?
    # Se não (isto é, seu nome não consta na tabela de variáveis já declaradas)
    if nome_variavel not in tabela:
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {id_no.linha}, "
            f"Coluna {id_no.coluna}\n\n"
            f"Variavel '{nome_variavel}' nao declarada."
        )
    
    # Obtendo da tabela o tipo da variável
    tipo_variavel = tabela[nome_variavel]["tipo"]
    # Inferindo o tipo da expressão em si
    tipo_expr = inferir_tipo(expr_no, tabela)

    # II - Segunda verificação: tipo com o qual a variável foi declarada é compatível com o valor que está sendo atribuído a ela?
    # Se não (isto é, o tipo da variável e da expressão não são compatíveis)
    if not tipos_compativeis(tipo_variavel, tipo_expr):
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr_no.linha}, "
            f"Coluna {expr_no.coluna}\n\n"
            f"Nao e possivel atribuir a variavel '{nome_variavel}', do tipo '{tipo_variavel}',\n"
            f"com valor da expressao do tipo '{tipo_expr}'."
        )

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subárvore de instrução de PRINT
def analisar_print(no, tabela):
    # Obtendo da subárvore:
    # o nó do nome da expressão em si sendo imprimida
    expr = no.filhos[0]

    # Inferindo o tipo da expressão em si
    tipo_expr = inferir_tipo(expr, tabela)

    # I - Verificação: tipo da expressão sendo impressão é 'string'?
    # Se não (isto é, se a expressão não é uma 'string')
    if tipo_expr not in ("bool", "int", "float", "string"):
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr.linha}, "
            f"Coluna {expr.coluna}\n\n"
            f"'print' aceita apenas expressoes do tipo\n"
            f"'bool', 'int', 'float' ou 'string'."
        )

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subárvore de instrução de WHILE
def analisar_while(no, tabela):
    # Obtendo da subárvore:
    # o nó da condiçao que faz o laço acontecer
    condicao = no.filhos[0]
    # o nó do bloco que acontece se a condição for satisfeita
    bloco = no.filhos[1]

    # Obtendo a expressão da condição de fato
    expr = condicao.filhos[0]
    # Inferindo o tipo da condição em si
    tipo_condicao = inferir_tipo(condicao, tabela)

    # I - Verificação: tipo da condição é booleano?
    # Se não (isto é, se a condição não for booleana)
    if tipo_condicao != "bool":
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr.linha}, "
            f"Coluna {expr.coluna}\n\n"
            f"A condicao do 'while' deve ser booleana, mas recebeu '{tipo_condicao}'."
        )

    # Então, analisa o bloco THEN
    analisar_bloco(bloco, tabela)

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subárvore de instruções de IF-ELSE
def analisar_ifelse(no, tabela):
    # Analisando cada um dos 3 tipos de instrução:
    for filho in no.filhos:
        # subsubárvore de instrução IF
        if filho.categoria == "IF":
            analisar_if(filho, tabela)

        # subsubárvore de instrução ELSEIF
        elif filho.categoria == "ELSEIF":
            analisar_elseif(filho, tabela)

        # subsubárvore de instrução ELSE
        elif filho.categoria == "ELSE":
            analisar_else(filho, tabela)

# Função que analisa uma subsubárvore de instrução de IF
def analisar_if(no, tabela):
    # Obtendo da subárvore:
    # o nó da condiçao que faz a verificação acontecer
    condicao = no.filhos[0]
    # o nó do bloco que acontece se a condição for satisfeita
    bloco = no.filhos[1]

    # Obtendo a expressão da condição de fato
    expr = condicao.filhos[0]
    # Inferindo o tipo da condição em si
    tipo_condicao = inferir_tipo(condicao, tabela)

    # I - Verificação: tipo da condição é booleano?
    # Se não (isto é, se a condição não for booleana)
    if tipo_condicao != "bool":
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr.linha}, "
            f"Coluna {expr.coluna}\n\n"
            f"A condicao do 'if' deve ser booleana, mas recebeu '{tipo_condicao}'."
        )

    # Então, analisa o bloco THEN
    analisar_bloco(bloco, tabela)

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subsubárvore de instrução de ELSEIF
def analisar_elseif(no, tabela):
    # Obtendo da subárvore:
    # o nó da condiçao que faz a checagem acontecer
    condicao = no.filhos[0]
    # o nó do bloco que acontece se a condição for satisfeita
    bloco = no.filhos[1]

    # Obtendo a expressão da condição de fato
    expr = condicao.filhos[0]
    # Inferindo o tipo da condição em si
    tipo_condicao = inferir_tipo(condicao, tabela)

    # I - Verificação: tipo da condição é booleano?
    # Se não (isto é, se a condição não for booleana)
    if tipo_condicao != "bool":
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {expr.linha}, "
            f"Coluna {expr.coluna}\n\n"
            f"A condicao do 'elseif' deve ser booleana, mas recebeu '{tipo_condicao}'."
        )

    # Então, analisa o bloco THEN
    analisar_bloco(bloco, tabela)

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subsubárvore de instrução de ELSE
def analisar_else(no, tabela):
    # Obtendo da subárvore:
    # o nó do bloco que acontece (quando todas as condições de IF e ELSEIF(s) falham)
    bloco = no.filhos[0]

    # Então, apenas analisa o bloco THEN
    analisar_bloco(bloco, tabela)

    # Caso não haja nenhum problema semântico, então, simplesmente continua a análise do resto do programa

# Função que analisa uma subárvore de instrução de BLOCO
def analisar_bloco(no, tabela):
    # Analisando todas as instruções dentro dele
    analisar_programa(no, tabela)

# Função que determinar se um valor de um tipo pode ser armazenado em uma variável de outro tipo
def tipos_compativeis(tipo_destino, tipo_origem):
    # Se ambos os tipos forem iguais, então, obviamente, eles são compatíveis
    if tipo_destino == tipo_origem:
        return True

    # Fora isso, a única promoção válida na linguagem é de INT para FLOAT
    # Exemplo: '3' automaticamente é interpretado como '3.0' (mesmo valor)
    if (tipo_destino == "float" and tipo_origem == "int"):
        return True
    # Observação: O contrário não é verdade: '3.5' não pode ser interpretado como um inteiro ('3' ou '4'?) (informação perdida)

    return False

# Função responsável por determinar qual é o tipo de uma determinada expressão
def inferir_tipo(no, tabela):
    categoria = no.categoria

    # Categoria: Literais: Se a expressão for apenas uma constante
    # INT: Se a expressão for apenas um número inteiro, então o tipo é INT
    if categoria == "INT":
        return "int"
    # FLOAT: Se a expressão for apenas um número ponto flutuante, então o tipo é FLOAT
    if categoria == "FLOAT":
        return "float"
    # STRING: Se a expressão for apenas uma string, então o tipo é STRING
    if categoria == "STRING":
        return "string"
    # BOOL: Se a expressão for apenas um bool, então o tipo é BOOL
    if categoria == "BOOL":
        return "bool"

    # Categoria: Variáveis: Se a expressão for apenas uma variável, então deve-se checar na tabela qual o tipo da variável
    if categoria == "ID":
        nome = no.valor

        # Se a variável da expressão nem estiver na tabela, significa que ela nem foi declarada
        if nome not in tabela:
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, Coluna {no.coluna}\n\n"
                f"Variavel '{nome}' nao declarada."
            )

        return tabela[nome]["tipo"]

    # Categoria: Condição: Se a expressão for uma condição, então deve-se inferir o tipo de seu filho
    if categoria == "CONDICAO":
        # Isto é, inferir recursivamente o tipo da expressão em si da condição
        return inferir_tipo(no.filhos[0], tabela)

    # Categoria: Operação numérica: Se a expressão for uma operação matemática, então deve-se inferir o tipo do valor da expressão em si
    if categoria in ("NUMOP_+-", "NUMOP_*/", "NUMOP_^"):
        # Isso é feito recursivamente,
        # inferindo o tipo do lado esquerdo
        tipo_esq = inferir_tipo(no.filhos[0], tabela)
        # e inferindo o tipo do lado direito
        tipo_dir = inferir_tipo(no.filhos[1], tabela)

        # Se os tipos dos operandos nem forem numéricos, não é nem possível operar com eles para verificar o tipo
        if(tipo_esq not in ("int", "float") or tipo_dir not in ("int", "float")):
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, Coluna {no.coluna}\n\n"
                f"Operacao numerica invalida entre '{tipo_esq}' e '{tipo_dir}'.\n"
                f"Operadores numericos exigem operandos do tipo 'int' e/ou 'float'."
            )

        # Se os tipos dos operandos forem válidos, e pelo menos um dos lados for um FLOAT
        if (tipo_esq == "float" or tipo_dir == "float"):
            # O tipo da operação será promovido a FLOAT
            return "float"

        # Se ambos os lados forem do tipo INT, então o resultado da operação será um INT
        return "int"


    # Categoria: Operação relacional: Se a expressão for uma comparação, então deve-se inferir o tipo do valor da expressão em si
    if categoria == "RELOP":
        # Isso é feito recursivamente,
        # inferindo o tipo do lado esquerdo
        tipo_esq = inferir_tipo(no.filhos[0], tabela)
        # e inferindo o tipo do lado direito
        tipo_dir = inferir_tipo(no.filhos[1], tabela)

        # Se ambos os lados forem numéricos, e, por consequência, comparáveis quanto ao seus valores
        if(tipo_esq in ("int", "float") and tipo_dir in ("int", "float")):
            # Então é uma comparação válida, que gerará uma resposta booleana (sim ou não)
            return "bool"

        # Se ambos os lados forem strings
        if(tipo_esq == "string" and tipo_dir == "string"):
            # Deve-se verificar se está fazendo uma operação válida entre elas
            operador = no.valor
            # As únicas comparações válidas entre strings são: '==' (IGUAL) e '!=' (DIFERENTE)
            # Se a operação não for nem de igualdade, nem de diferença
            if operador not in ( "==", "!="):
                # Então trata-se de um erro semântico, o qual é comunicado à main
                raise Exception(
                    f"ERRO SEMANTICO:\n"
                    f"Linha {no.linha}, Coluna {no.coluna}\n\n"
                    f"Comparacoes entre 'strings' apenas aceitam '==' ou '!='."
                )
            # (Obs.: Não é possível comparar strings com '<', '>', '<=', '>=')

            # Se for uma comparação válida entre strings,
            # então gerará uma resposta booleana (sim ou não)
            return "bool"

        # Se os dois lados nem forem compatíveis de se comparar
        # Então trata-se de um erro semântico, o qual é comunicado à main
        raise Exception(
            f"ERRO SEMANTICO:\n"
            f"Linha {no.linha}, Coluna {no.coluna}\n\n"
            f"Comparacao invalida entre '{tipo_esq}' e '{tipo_dir}'."
        )

    # Categoria: Operação lógica: Se a expressão for uma operação booleana
    # AND: Se a expressão for um AND, então deve-se inferir o tipo do valor da expressão em si
    if categoria == "LOGIC_AND":
        # Isso é feito recursivamente,
        # inferindo o tipo do lado esquerdo
        tipo_esq = inferir_tipo(no.filhos[0], tabela)
        # e inferindo o tipo do lado direito
        tipo_dir = inferir_tipo(no.filhos[1], tabela)

        # Se os dois lados não forem booleanos
        if(tipo_esq != "bool" or tipo_dir != "bool"):
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, Coluna {no.coluna}\n\n"
                f"Operador '&' exige operandos booleanos."
            )

        # Se for uma operação lógica válida
        # então gerará uma resposta booleana
        return "bool"

    # OR: Se a expressão for um OR, então deve-se inferir o tipo do valor da expressão em si
    if categoria == "LOGIC_OR":
        # Isso é feito recursivamente,
        # inferindo o tipo do lado esquerdo
        tipo_esq = inferir_tipo(no.filhos[0], tabela)
        # e inferindo o tipo do lado direito
        tipo_dir = inferir_tipo(no.filhos[1], tabela)

        # Se os dois lados não forem booleanos
        if(tipo_esq != "bool" or tipo_dir != "bool"):
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, Coluna {no.coluna}\n\n"
                f"Operador '|' exige operandos booleanos."
            )

        # Se for uma operação lógica válida
        # então gerará uma resposta booleana
        return "bool"


    # NOT: Se a expressão for um NOT, então deve-se inferir o tipo do valor da expressão em si
    if categoria == "LOGIC_NOT":
        # Isso é feito recursivamente,
        # inferindo o tipo da expressão a ser negada
        tipo = inferir_tipo(no.filhos[0], tabela)

        # Se a expressão não for booleana
        if tipo != "bool":
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, "
                f"Coluna {no.coluna}\n\n"
                f"Operador '!' exige operando booleano."
            )

        # Se for uma operação lógica válida
        # então gerará uma resposta booleana
        return "bool"

    # Categoria: Expressão unária: Se a expressão for uma operação unária
    # + Unário: Se a expressão for um UNARIO +, então deve-se inferir o tipo do valor do operando
    if categoria == "UNARIO_+":
        # Isso é feito recursivamente,
        # inferindo o tipo do operando em si
        tipo = inferir_tipo(no.filhos[0], tabela)

        # Se o tipo do operando não for numérico, não é possível realizar uma operação unária
        if tipo not in ("int", "float"):
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, "
                f"Coluna {no.coluna}\n\n"
                f"Operador '+' unario exige operando 'int' e/ou 'float'."
            )

        # Se for uma operação unária válida, o resultado do tipo permanece não se altera
        return tipo
    
    # - Unário: Se a expressão for um UNARIO -, então deve-se inferir o tipo do valor do operando
    if categoria == "UNARIO_-":
        # Isso é feito recursivamente,
        # inferindo o tipo do operando em si
        tipo = inferir_tipo(no.filhos[0], tabela)

        # Se o tipo do operando não for numérico, não é possível realizar uma operação unária
        if tipo not in ("int", "float"):
            # Então trata-se de um erro semântico, o qual é comunicado à main
            raise Exception(
                f"ERRO SEMANTICO:\n"
                f"Linha {no.linha}, "
                f"Coluna {no.coluna}\n\n"
                f"Operador '-' unario exige operando do tipo 'int' e/ou 'float'."
            )

        # Se for uma operação unária válida, o resultado do tipo permanece não se altera
        return tipo


    raise Exception(
        f"ERRO INTERNO:\n"
        f"Categoria desconhecida: "
        f"{categoria}"
    )