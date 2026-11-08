#########################################################################################################################################
### CÓDIGO ABSTRACT SYNTAX TREE (AST) - LINGUAGEM <SHODAN>                                                                            ###
#########################################################################################################################################

# Classe de um nó da AST (terminal ou não-terminal)
class NoAST:
    def __init__(self, categoria, valor=None, linha=None, coluna=None):
        # Categoria do nó
        self.categoria = categoria
        # Valor do nó
        self.valor = valor
        # Linha do nó
        self.linha = linha
        # Coluna do nó
        self.coluna = coluna
        # Filhos que derivam do nó
        self.filhos = []

# Função recursiva de impressão da árvore sintática
# "no" é o nó atual a ser impresso; "prefixo" guarda os espaços e barras, acumulativamente; "ultimo" é a variável que indica se o filho atual é o último
def imprimir_ast(no, prefixo="", ultimo=True):
    # Decide a barra de conexão a ser impressa, a depender se o filho atual sendo impresso é o último ou não
    conector = "└── " if ultimo else "├── "

    # Decide se o nó atual é um terminal (token) ou não-terminal
    # Se for terminal, ele possui um valor associado, que será impresso junto à categoria
    if no.valor is not None:
        texto = f"{no.categoria}: {no.valor}"
    # Senão, será impresso apenas a categoria do não-terminal
    else:
        texto = no.categoria

    # Impressão de fato, das barras conectando o nó ao seu pai, e do nó em si
    print(prefixo + conector + texto)

    # Se o nó atual é o último filho, a barra se trata de espaços vazios, porque não haverá mais irmãos abaixo
    # Senão se ele não é o último filho, há necessidade da barra ser um galho, pois haverá mais irmãos abaixo do nó
    novo_prefixo = prefixo + ("    " if ultimo else "│   ")

    # Percorre os filhos do nó atual
    for i, filho in enumerate(no.filhos):
        # E chama a impressão recursivamente para eles
        imprimir_ast(
            filho,
            novo_prefixo,
            i == len(no.filhos) - 1
        )


# FUNÇÃO PRINCIPAL, de construção da AST (Abstract Syntax Tree)
#########################################################################################################################################
# Recebe a parse tree (árvore sintática) e constrói a AST com base nela
def construir_ast(arvore_sintatica):
    # Retorna à main a AST construída
    return construir_programa_gramatica(arvore_sintatica)

# A AST não inicia-se no nó "PROGRAMA GRAMÁTICA" (símbolo inicial), mas no nó "PROGRAMA"
def construir_programa_gramatica(no):
    # O primeiro e único nó, "PROGRAMA", inicia todo o processo
    programa = no.filhos[0]

    # e "PROGRAMA" passa a ser a raiz da AST 
    return construir_programa(programa)

# Construção da AST em si, abstraindo a parse tree
def construir_programa(no):
    # O nó "PROGRAMA" é a raiz da AST, e pai de todos os programas do código
    raiz = NoAST("PROGRAMA")

    # Percorrendo a árvore recursivamente
    while True:
        # Caso de parada: acabaram as instruções do PROGRAMA
        if len(no.filhos) == 1 and no.filhos[0].nome == "ε":
            # Então interrompe o laço
            break

        # Obtém a instrução atual
        instrucao = no.filhos[0]

        
        # Dispachando para o tipo de instrução, seguindo a lógica da gramática:
        
        # Instrução de declaração
        if instrucao.nome == "[DECLARACAO]":
            raiz.filhos.append(construir_declaracao(instrucao))

        # Instrução de atribuição
        elif instrucao.nome == "[ATRIBUICAO]":
            raiz.filhos.append(construir_atribuicao(instrucao))

        # Instrução de impressão
        elif instrucao.nome == "[IMPRESSAO]":
            raiz.filhos.append(construir_impressao(instrucao))

        # Instrução de cadeia if-else
        elif instrucao.nome == "[IF-ELSE]":
            raiz.filhos.append(construir_ifelse(instrucao))

        # Instrução de laço while
        elif instrucao.nome == "[WHILE]":
            raiz.filhos.append(construir_while(instrucao))

        # Acessa o nó da próxima instrução
        no = no.filhos[1]

    # Ao fim, retorna a AST a partir do nó pai de todos, "PROGRAMA"
    return raiz

# A partir daqui, inicia-se a filosofia da AST, abstraindo partes das respectivas instruções,
# removendo símbolos sintáticos desnecessários e mantendo apenas a informação semanticamente relevante

# Função de construir a abstração da "DECLARAÇÃO"
def construir_declaracao(no):
    # Uma "DECLARAÇÃO" é da forma: <tipo> <id> <atribuicao> [EXPRESSÃO] <finalizador>
    # Exemplo: int x = 2 ;
    
    # Desses cinco componentes, apenas três interessam:
    # o tipo da variável (no exemplo acima o tipo é 'inteiro'),
    tipo_token = no.filhos[0]
    # o nome da variável (no exemplo acima a variável chama-se 'x'),
    id_token = no.filhos[1]
    # e a expressão em si cujo resultado está sendo atribuído à variável (no exemplo acima '2')
    expr = no.filhos[3]
    # (os outros dois elementos são apenas relevante à parte sintática, da gramática)

    # Criação do nó pai, que define que virá em seguida uma "DECLARAÇÃO", e seus filhos
    raiz = NoAST(
        categoria="DECLARACAO",
        linha=id_token.linha,
        coluna=id_token.coluna
    )

    # Os filhos serão justamente os elementos que importam à AST

    # Cria o filho "TIPO" da variável declarada
    raiz.filhos.append(
        NoAST(
            categoria="TIPO",
            valor=tipo_token.valor,     # Salvando qual é o tipo em si (int, float, string)
            linha=tipo_token.linha,     # Salvando a linha inicial onde foi definido o token tipo
            coluna=tipo_token.coluna    # Salvando a coluna inicial onde foi definido o token tipo
        )
    )

    # Cria o filho "ID", o nome da variável declarada
    raiz.filhos.append(
        NoAST(
            categoria="ID",
            valor=id_token.valor,       # Salvando qual é o nome da variável
            linha=id_token.linha,       # Salvando a linha inicial onde foi definido o nome da variável
            coluna=id_token.coluna      # Salvando a coluna inicial onde foi definido o nome da variável
        )
    )

    # Cria aqui, recursivamente, o filho que será o resultado da expressão em si,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    raiz.filhos.append(construir_expressao(expr))

    # Por fim retorna a subárvore do nó pai "DECLARAÇÃO" com seus filhos
    return raiz

# Função de construir a abstração da "ATRIBUIÇÃO"
def construir_atribuicao(no):
    # Uma "ATRIBUIÇÃO" é da forma: <id> <atribuicao> [EXPRESSÃO] <finalizador>
    # Exemplo: x = 3;
    
    # Desses quatro componentes, apenas dois interessam:
    # o nome da variável (no exemplo acima a variável chama-se 'x'),
    id_token = no.filhos[0]
    # e a expressão em si cujo resultado está sendo atribuído à variável (no exemplo acima '3')
    expr = no.filhos[2]
    # (os outros dois elementos são apenas relevante à parte sintática, da gramática)

    # Criação do nó pai, que define que virá em seguida uma "ATRIBUIÇÃO", e seus filhos
    raiz = NoAST(
        categoria="ATRIBUICAO",
        linha=id_token.linha,
        coluna=id_token.coluna
    )

    # Os filhos serão justamente os elementos que importam à AST

    # Cria o filho "ID", o nome da variável a ser feita a atribuição
    raiz.filhos.append(
        NoAST(
            categoria="ID",
            valor=id_token.valor,   # Salvando qual é o nome da variável
            linha=id_token.linha,   # Salvando a linha inicial onde foi dita o nome da variável
            coluna=id_token.coluna  # Salvando a coluna inicial onde foi dita o nome da variável
        )
    )

    # Cria aqui, recursivamente, o filho que será o resultado da expressão em si,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    raiz.filhos.append(construir_expressao(expr))

    # Por fim retorna a subárvore do nó pai "ATRIBUICAO" com seus filhos
    return raiz

# Função de construir a abstração da IMPRESSÃO "PRINT"
def construir_impressao(no):
    # Um "PRINT" é da forma: <print> <paropen> [EXPRESSÃO] <parclose> <finalizador>
    # Exemplo: print("hello");

    # Desses cinco componentes, apenas um interessa:
    # a expressão que vai ser impressa de fato
    expr = no.filhos[2]
    # (a palavra 'print' já é ditada pelo nome do pai, e os outros elementos são apenas relevante à parte sintática, da gramática)

    print_token = no.filhos[0]
    # Criação do nó pai, que define que virá em seguida uma impressão "PRINT", e seu filho
    raiz = NoAST(
        categoria="PRINT",
        linha=print_token.linha,
        coluna=print_token.coluna
    )

    # Cria aqui, recursivamente, o filho que será o resultado da expressão em si,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    raiz.filhos.append(construir_expressao(expr))

    # Por fim retorna a subárvore do nó pai "PRINT" com seus filhos
    return raiz

# Função de construir a abstração do LAÇO "WHILE"
def construir_while(no):
    # Um "WHILE" é da forma: <while> <paropen> [EXPRESSÃO] <parclose> [THEN]
    # Exemplo: while(x>0){x = x-1;}

    # Desses cinco componentes, apenas dois interessam:
    # a condição em si que faz o laço rodar
    expr = no.filhos[2]
    # e o bloco que acontece se a condição for satisfeita (THEN)
    then = no.filhos[4]
    #(a palavra 'while' já é ditada pelo nome do pai, e os outros elementos são apenas relevante à parte sintática, da gramática)

    while_token = no.filhos[0]
    # Criação do nó pai, que define que virá em seguida um laço "WHILE", e seus filhos
    raiz = NoAST(
        categoria = "WHILE",
        linha=while_token.linha,
        coluna=while_token.coluna
    )

    # Cria o filho "CONDIÇÃO" que faz o laço rodar
    condicao = NoAST("CONDICAO")
    # E cria, recursivamente, o filho do filho que será o resultado da expressão em si da condição,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    condicao.filhos.append(construir_expressao(expr))
    # E o nó "CONDIÇÃO", e seus filhos, derivarão do nó pai "WHILE"
    raiz.filhos.append(condicao)
    
    # Cria aqui, recursivamente, o filho que será o bloco a ser executado enquanto a condição se satisfizer,
    # podendo ser qualquer nova instrução do programa
    raiz.filhos.append(construir_then(then))

    # Por fim retorna a subárvore do nó pai "WHILE" com seus filhos
    return raiz

# Função de construir a abstração da CADEIA "IF-ELSEIF-ELSE"
def construir_ifelse(no):
    # Criação do nó pai, que define que virá em seguida uma cadeia "IF_ELSE", e seu(s) filho(s)
    raiz = NoAST("IF_ELSE")

    # Cria aqui, recursivamente, o filho que será o primeiro IF,
    # o qual é o único que é obrigatório (e há apenas um na cadeia, no começo dela)
    raiz.filhos.append(construir_if(no.filhos[0]))

    # Cria aqui, recursivamente, a sequência de filhos que serão os ELSEIFs,
    # os quais podem ser de 0 (nenhum ELSEIF) a N (inúmeros ELSEIFS)
    raiz.filhos.extend(construir_elseifs(no.filhos[1]))

    # Cria aqui, recursivamente, o filho que será o último ELSE,
    # o qual pode ser 0 (nenhum ELSE) ou, se houver, apenas um na cadeia, no final dela
    else_ast = construir_else(no.filhos[2])
    # e, se o ELSE não for vazio (houver um ELSE),
    if else_ast is not None:
        # o filho ELSE é adicionado ao pai
        raiz.filhos.append(else_ast)

    # Por fim retorna a subárvore do nó pai "IF_ELSE" com seus filhos
    return raiz

# Função de construir o primeiro "IF" da cadeia IF-ELSEIF-ELSE
def construir_if(no):
    # Um "IF" é da forma: <if> <paropen> [EXPRESSÃO] <parclose> [THEN]
    # Exemplo: if(x>0){x = x-1;}

    # Desses cinco componentes, apenas dois interessam:
    # a condição em si que faz o bloco acontecer
    expr = no.filhos[2]
    # e o bloco que acontece se a condição for satisfeita (THEN)
    then = no.filhos[4]
    #(a palavra 'if' já é ditada pelo nome do pai, e os outros elementos são apenas relevante à parte sintática, da gramática)

    if_token = no.filhos[0]
    # Criação do nó pai, que define que virá em seguida um condicional "IF", e seus filhos
    raiz = NoAST(
        categoria="IF",
        linha=if_token.linha,
        coluna=if_token.coluna
    )

    # Cria o filho "CONDIÇÃO" que faz o laço rodar
    condicao = NoAST("CONDICAO")
    # E cria, recursivamente, o filho do filho que será o resultado da expressão em si da condição,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    condicao.filhos.append(construir_expressao(expr))
    # E o nó "CONDIÇÃO", e seus filhos, derivarão do nó pai "IF"
    raiz.filhos.append(condicao)

    # Cria aqui, recursivamente, o filho que será o bloco a ser executado se a condição se satisfizer,
    # podendo ser qualquer nova instrução do programa
    raiz.filhos.append(construir_then(then))

    # Por fim retorna a subárvore do nó pai "IF" com seus filhos
    return raiz

# Função de construir a lista de ELSEIFS da cadeia IF-ELSEIF-ELSE
def construir_elseifs(no):
    # A lista é inicializada vazia (nenhum "ELSEIF")
    lista = []

    # E enquanto houverem (se houver algum) "ELSEIF"s não nulos
    while not(len(no.filhos) == 1 and no.filhos[0].nome == "ε"):
        # Cria aqui, recursivamente, cada ELSEIF
        lista.append(construir_elseif(no.filhos[0]))
        # e verifica se há mais ELSEIFs
        no = no.filhos[1]

    # Por fim retorna a subárvore do nó pai "IF" com seus filhos
    return lista

# Função de construir cada "ELSEIF" da cadeia IF-ELSEIF-ELSE
def construir_elseif(no):
    # Um "ELSEIF" é da forma: <elseif> <paropen> [EXPRESSÃO] <parclose> [THEN]
    # Exemplo: elseif(x>0){x = x-1;}

    # Desses cinco componentes, apenas dois interessam:
    # a condição em si que faz o bloco acontecer
    expr = no.filhos[2]
    # e o bloco que acontece se a condição for satisfeita (THEN)
    then = no.filhos[4]
    #(a palavra 'elseif' já é ditada pelo nome do pai, e os outros elementos são apenas relevante à parte sintática, da gramática)

    elseif_token = no.filhos[0]
    # Criação do nó pai, que define que virá em seguida um condicional "ELSEIF", e seus filhos
    raiz = NoAST(
        categoria="ELSEIF",
        linha=elseif_token.linha,
        coluna=elseif_token.coluna
    )

    # Cria o filho "CONDIÇÃO" que faz o laço rodar
    condicao = NoAST("CONDICAO")
    # E cria, recursivamente, o filho do filho que será o resultado da expressão em si da condição,
    # seja uma expressão primária, unária, ou uma expressão com mais de um operando
    condicao.filhos.append(construir_expressao(expr))
    # E o nó "CONDIÇÃO", e seus filhos, derivarão do nó pai "IF"
    raiz.filhos.append(condicao)

    # Cria aqui, recursivamente, o filho que será o bloco a ser executado se a condição se satisfizer,
    # podendo ser qualquer nova instrução do programa
    raiz.filhos.append(construir_then(then))

    # Por fim retorna a subárvore do nó pai "ELSEIF" com seus filhos
    return raiz

# Função de construir o último "ELSE" da cadeia IF-ELSEIF-ELSE
def construir_else(no):
    # Se não há "ELSE" no final
    if (len(no.filhos) == 1 and no.filhos[0].nome == "ε"):
        # Simplesmente retorna nulo
        return None

    # Se há um "ELSE" no final da cadeia,
    # Um "ELSE" é da forma: <else> [THEN]
    # Exemplo: else{x = x-1;}

    # Desses dois componentes, apenas um interessa:
    # o bloco que acontece (se nenhum dos if,elseif for se satisfizer) (THEN)
    then = no.filhos[1]
    #(a palavra 'else' já é ditada pelo nome do pai)

    else_token = no.filhos[0]
    # Criação do nó pai, que define que virá em seguida um condicional "ELSE", e seu filho
    raiz = NoAST(
        categoria="ELSE",
        linha=else_token.linha,
        coluna=else_token.coluna
    )

    # Cria aqui, recursivamente, o filho que será o bloco a ser executado se a condição se satisfizer,
    # podendo ser qualquer nova instrução do programa
    raiz.filhos.append(construir_then(then))

    # Por fim retorna a subárvore do nó pai "ELSE" com seu filho
    return raiz

# Função de construir o "BLOCO" THEN que acontece se, ou enquanto, uma condição for satisfeita
def construir_then(no):
    # Um "BLOCO" THEN é da forma: <chaopen> [PROGRAMA] <chaclose>
    # Desses três componentes, apenas um interessa:
    # a(s) instrução(ões) que é(são) executada(s) se, ou enquanto, a condição for satisfeita 
    programa = no.filhos[1]

    # Criação do nó pai, que define que virá em seguida um "BLOCO", e seu(s) filho(s) (se houver algum)
    bloco = NoAST("BLOCO")

    # Cria aqui, recursivamente, o(s) filho(s) (se houver algum) (a(s) instrução(ões) que é(são) executada(s))
    # podendo ser qualquer nova instrução (ou conjunto de instruções) do programa
    programa_ast = construir_programa(programa)

    # E adiciona o(s) filho(s) do filho "PROGRAMA" (se houver)
    bloco.filhos.extend(programa_ast.filhos)

    # Por fim retorna a subárvore do nó pai "THEN" com seu(s) filho(s) (se houver)
    return bloco

# A partir daqui, a AST fará a sua principal reestruturação sobre as expressões,
# abstraindo toda a recursividade dos nós intermediários da gramática

# o nó "EXPRESSÃO" é apenas um intermediário inicial, então é imediatamente eliminado
def construir_expressao(no):
    return construir_expr_or(no.filhos[0])
# E a sequência será seguindo a ordem de precedência

# A menor precedência é da operação OR
def construir_expr_or(no):
    esquerda = construir_expr_and(no.filhos[0])

    return construir_expr_or_linha(esquerda, no.filhos[1])

# Uma operação OR de fato
def construir_expr_or_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_OR'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador '|'
    operador = no.filhos[0]
    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    direita = construir_expr_and(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "LOGIC_OR", e seus filhos
    raiz = NoAST(
        categoria="LOGIC_OR",
        valor=operador.valor,   # Salvando que a operação é um OR ('|')
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "LOGIC_OR" com seus filhos
    return construir_expr_or_linha(raiz, no.filhos[2])

# A segunda menor precedência é da operação AND
def construir_expr_and(no):
    esquerda = construir_expr_relacional(no.filhos[0])

    return construir_expr_and_linha(esquerda, no.filhos[1])

# Uma operação AND de fato
def construir_expr_and_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_AND'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador '&'
    operador = no.filhos[0]
    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    direita = construir_expr_relacional(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "LOGIC_AND", e seus filhos
    raiz = NoAST(
        categoria="LOGIC_AND",
        valor=operador.valor,   # Salvando que a operação é um AND ('&')
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "LOGIC_AND" com seus filhos
    return construir_expr_and_linha(raiz, no.filhos[2])

# A precedência intermediária, entre operações booleanas e matemáticas, é de uma operação RELACIONAL
def construir_expr_relacional(no):
    esquerda = construir_expr_somasub(no.filhos[0])

    return construir_expr_relacional_linha(esquerda, no.filhos[1])

# Uma operação RELACIONAL de fato
def construir_expr_relacional_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_RELACIONAL'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador relacional (todos tem a mesma precedência entre si)
    operador = no.filhos[0]

    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    direita = construir_expr_somasub(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "RELOP", e seus filhos
    raiz = NoAST(
        categoria="RELOP",
        valor=operador.valor,   # Salvando qual é o operador relacional
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "RELOP" com seus filhos
    return raiz

# A precedência acima de uma operação relacional é a operação numérica, dentre as quais a menor é a soma/subtração
def construir_expr_somasub(no):
    esquerda = construir_expr_muldiv(no.filhos[0])

    return construir_expr_somasub_linha(esquerda, no.filhos[1])

# Uma operação de SOMA/SUBTRAÇÃO de fato
def construir_expr_somasub_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_SOMASUB'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador matemático (seja soma '+' ou subtração '-') (ambos tem a mesma precedência entre si)
    operador = no.filhos[0]

    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    direita = construir_expr_muldiv(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "NUMOP_+-", e seus filhos
    raiz = NoAST(
        categoria="NUMOP_+-",
        valor=operador.valor,   # Salvando qual é o operador matemático
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "NUMOP_+-" com seus filhos
    return construir_expr_somasub_linha(raiz, no.filhos[2])

# A precedência, dentre as operações numéricas, intermediária, é a multiplicação/divisão
def construir_expr_muldiv(no):
    esquerda = construir_expr_pot(no.filhos[0])

    return construir_expr_muldiv_linha(esquerda, no.filhos[1])

# Uma operação de MULTIPLICAÇÃO/DIVISÃO de fato
def construir_expr_muldiv_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_MULDIV'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador matemático (seja multiplicação '*' ou divisão '/') (ambos tem a mesma precedência entre si)
    operador = no.filhos[0]

    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    direita = construir_expr_pot(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "NUMOP_*/", e seus filhos
    raiz = NoAST(
        categoria="NUMOP_*/",
        valor=operador.valor,   # Salvando qual é o operador matemático
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "NUMOP_*/" com seus filhos
    return construir_expr_muldiv_linha(raiz, no.filhos[2])

# A maior precedência, dentre as operações numéricas, é a da potenciação
def construir_expr_pot(no):
    esquerda = construir_expr_unario(no.filhos[0])

    return construir_expr_pot_linha(esquerda, no.filhos[1])

# Uma operação de POTENCIAÇÃO de fato
def construir_expr_pot_linha(esquerda, no):
    # Se a árvore toda à esquerda já está pronta, [EXPR_POT'] é vazio
    if no.filhos[0].nome == "ε":
        # Então simplesmente retorna a árvore à esquerda
        return esquerda

    # Senão, salva o operador '^'
    operador = no.filhos[0]

    # E cria, recursivamente, o filho da direita, que será o resultado da expressão à direita
    # (observação importante: o filho à direita não é [EXPR_POT'], mas [EXPR_POT])
    # (isso por conta da propriedade matemática da associação à direita da potenciação)
    direita = construir_expr_pot(no.filhos[1])

    # Cria o nó pai, que define que virá uma EXPRESSÃO "NUMOP_^", e seus filhos
    raiz = NoAST(
        categoria="NUMOP_^",
        valor=operador.valor,   # Salvando que é o operador matemático '^'
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona os filhos operandos da esquerda e da direita
    raiz.filhos.append(esquerda)
    raiz.filhos.append(direita)

    # Por fim retorna a subárvore do nó pai "NUMOP_^" com seus filhos
    return raiz

# A segunda maior precedência de todas é de uma operação UNARIA
def construir_expr_unario(no):
    # Se a expressão é composta por apenas um único operando (sem operadores),
    if len(no.filhos) == 1:
        # Então apenas trata-se de uma operação primária
        return construir_expr_primario(no.filhos[0])

    # Senão, salva o operador unário
    operador = no.filhos[0]

    # Se a operação é uma negação lógica
    if operador.valor == "!":
        categoria = "LOGIC_NOT"

    # Se a operação é um sinal de '+' na frente do operando
    elif operador.valor == "+":
        categoria = "UNARIO_+"

    # Se a operação é um sinal de '-' na frente do operando
    elif operador.valor == "-":
        categoria = "UNARIO_-"

    raiz = NoAST(
        categoria=categoria,
        valor=operador.valor,   # Salvando qual é o operador unário (negação ou sinal do operando)
        linha=operador.linha,   # Salvando a linha inicial da operação
        coluna=operador.coluna  # Salvando a coluna inicial da operação
    )

    # E adiciona o filho operando
    raiz.filhos.append(construir_expr_unario(no.filhos[1]))

    # Por fim retorna a subárvore do nó pai "UNARIO" com seu filho
    return raiz

# A maior precedência de todas é de uma operação PRIMARIA
def construir_expr_primario(no):
    primeiro = no.filhos[0]

    # Se a operação primária for do tipo <paropen> [EXPRESSAO] <parclose>
    # Ex.: (5+3^2)
    if primeiro.nome == "<PAROPEN>":
        # Então retorna, sobre maior precedência na árvore, a expressão contida dentro dos parênteses
        return construir_expressao(no.filhos[1])

    # Senão se for apenas uma variável
    elif primeiro.nome == "<ID>":
        # Cria o nó que define que virá uma VARIAVEL "ID"
        return NoAST(
            categoria="ID",
            valor=primeiro.valor,   # Salvando qual é o nome da variável
            linha=primeiro.linha,   # Salvando a linha inicial da variável
            coluna=primeiro.coluna  # Salvando a coluna inicial da variável
        )

    # Senão, trata-se de um literal (inteiro, ponto flutuante ou string)
    else:
        token = primeiro.filhos[0]

        if token.nome == "<INT>":
            return NoAST(
                categoria="INT",
                valor=int(token.valor),
                linha=token.linha,
                coluna=token.coluna
            )

        # FLOAT
        elif token.nome == "<FLOAT>":
            return NoAST(
                categoria="FLOAT",
                valor=float(token.valor),
                linha=token.linha,
                coluna=token.coluna
            )

        # STRING
        elif token.nome == "<STRING>":
            return NoAST(
                categoria="STRING",
                valor=token.valor,
                linha=token.linha,
                coluna=token.coluna
            )