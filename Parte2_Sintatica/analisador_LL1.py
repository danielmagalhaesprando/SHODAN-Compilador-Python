#########################################################################################################################################
### CÓDIGO ANALISADOR SINTÁTIO LL(1) - LINGUAGEM <SHODAN>                                                                                               ###
#########################################################################################################################################

from .tabela_parsing import construir_tabela


# Classe de um nó da árvore sintática (terminal ou não-terminal)
class No:
    def __init__(self, nome):
        # Símbolo do nó
        self.nome = nome
        # Valor do nó
        self.valor = None
        # Linha do nó
        self.linha = None
        # Coluna do nó
        self.coluna = None
        # Filhos que derivam do nó
        self.filhos = []

# Função recursiva de impressão da árvore sintática
# "no" é o nó atual a ser impresso; "prefixo" guarda os espaços e barras, acumulativamente; "ultimo" é a variável que indica se o filho atual é o último
def imprimir_arvore(no, prefixo="", ultimo=True):
    # Decide a barra de conexão a ser impressa, a depender se o filho atual sendo impresso é o último ou não
    conector = "└── " if ultimo else "├── "

    # Impressão de fato, das barras conectando o nó ao seu pai, e do nó em si
    print(prefixo + conector + no.nome)

    # Se o nó atual é o último filho, a barra se trata de espaços vazios, porque não haverá mais irmãos abaixo
    # Senão se ele não é o último filho, há necessidade da barra ser um galho, pois haverá mais irmãos abaixo do nó
    novo_prefixo = prefixo + ("    " if ultimo else "│   ")

    # Percorre os filhos do nó atual
    for i, filho in enumerate(no.filhos):
        # E chama a impressão recursivamente para eles
        imprimir_arvore(
            filho,
            novo_prefixo,
            i == len(no.filhos) - 1
        )


# Dicionário usado em erros sintáticos para dizer o que cada token significa
DIC_TOKENS = {
    "<ID>": "identificador / variável",
    "<INT>": "numero inteiro",
    "<FLOAT>": "numero fracionário",
    "<STRING>": "texto/string",
    "<PAROPEN>": "'(' (abertura de parenteses)",
    "<PARCLOSE>": "')' (fechamento de parenteses)",
    "<CHAOPEN>": "'{' (abertura de bloco)",
    "<CHACLOSE>": "'}' (fechamento de bloco)",
    "<FINALIZADOR>": "';' (fim de instrucao)",
    "<ATRIBUICAO>": "'=' (operador de atribuicao)",
    "<RELOP>": "operador relacional",
    "<LOGIC_AND>": "'&' (operador logico AND)",
    "<LOGIC_OR>": "'|' (operador logico OR)",
    "<LOGIC_NOT>": "'!' (negacao logica)",
    "<NUMOP_+->": "operador '+' ou '-'",
    "<NUMOP_*/>": "operador '*' ou '/'",
    "<NUMOP_^>": "'^' (potenciacao)",
    "<IF>": "palavra reservada 'if'",
    "<ELSE>": "palavra reservada 'else'",
    "<ELSEIF>": "palavra reservada 'elseif'",
    "<WHILE>": "palavra reservada 'while'",
    "<PRINT>": "palavra reservada 'print'",
    "<TIPO>": "tipo de variavel"
}


# PROCESSAMENTO PRINCIPAL - ALGORITMO DE PARSING LL(1):
#########################################################################################################################################
# Recebe como entrada a lista de tokens produzida pelo Analisador léxico
def parser_ll1(lista_tokens):
    # Tabela de parsing, que vai dizer qual produção usar se vir dado token
    tabela, SIMBOLO_INICIAL = construir_tabela()

    # Log de execução utilizado para armazenar MATCHes, derivações e o estado da pilha, ao decorrer da execução
    log = []

    # Copia a entrada de tokens, para evitar alterar a original
    entrada = lista_tokens.copy()

    # Adiciona o marcador de fim "$" ao final da entrada
    entrada.append({
        "nome": "$",
        "valor": "$",
        "linha": -1,
        "coluna": -1
    })


    # Pilha sintática:
    pilha = ["$", SIMBOLO_INICIAL]

    # Pilha da árvore:
    # Raiz da árvore sintática
    raiz = No(SIMBOLO_INICIAL)
    # Sincronizada com a pilha da árvore
    pilha_nos = [No("$"), raiz]


    indice = 0
    # O analisador funciona desempilhando, empilhando e derivando os símbolos da pilha
    # Enquanto houver símbolos a serem derivados na pilha
    while pilha:
        # Salva o estado atual da pilha
        log.append(f"PILHA: {pilha}")

        # Desempilha o símbolo no topo da pilha sintática
        topo = pilha.pop()
        # E, semelhantemente, o da pilha da árvore
        no_atual = pilha_nos.pop()

        # Token atual sendo lido na entrada
        token_atual = entrada[indice]

        # Se faltar um token no final, salva onde faltou
        if token_atual["nome"] == "$":
            token_erro = entrada[indice - 1]

        # Senão, o erro estará no atual mesmo
        else:
            token_erro = token_atual

        # Salva qual é o token atual sendo lido
        atual = token_atual["nome"]


        # Caso 1: Se o símbolo desempilhado da pilha for um terminal (um token), ou se a pilha estiver vazia
        if topo.startswith("<") or topo == "$":
            # Se era o esperado na entrada
            if topo == atual:
                # Salva informações léxicas no nó terminal
                no_atual.valor = token_atual["valor"]
                no_atual.linha = token_atual["linha"]
                no_atual.coluna = token_atual["coluna"]
                
                # Salva no log que houve consonância com o esperado
                log.append(f"MATCH: {topo}")

                # Então consome o token de entrada
                indice += 1

            # Senão, significa um ERRO SINTÁTICO, o qual é comunicado à main
            else:
                if atual == "$":
                    lexema_encontrado = "EOF (fim da entrada)"
                else:
                    lexema_encontrado = token_atual["valor"]
                
                raise Exception(
                        f"ERRO SINTATICO:\n"
                        f"Linha {token_erro['linha']}, "
                        f"Coluna {token_erro['coluna']}\n\n"

                        f"Esperado: {topo}\n"
                        f"Descricao: {DIC_TOKENS.get(topo,'token desconhecido')}\n\n"

                        f"Token encontrado: {atual}\n"
                        f"Lexema encontrado: {lexema_encontrado}"
                    )

        # Caso 2: Se o símbolo desempilhado da pilha for um não-terminal (uma regra)
        else:
            # Para o caso de ocorrer algum erro interno
            if topo not in tabela:
                raise Exception(
                    f"ERRO INTERNO:\n"
                    f"Nao-terminal inexistente na tabela LL(1): {topo}"
                )

            # Se o token de lookahead visto atualmente na entrada não possui correspondência válida para o não-terminal atual desempilhado, na tabela
            # Significa que a regra não não possui nenhuma derivação que comece (FIRST) com aquele token
            if atual not in tabela[topo]:
                esperados = tabela[topo].keys()

                # Ou seja, significa um ERRO SINTÁTICO, o qual é comunicado à main
                if atual == "$":
                    lexema_encontrado = "EOF (fim da entrada)"
                else:
                    lexema_encontrado = token_atual["valor"]

                esperados = tabela[topo].keys()

                raise Exception(
                    f"ERRO SINTATICO:\n"
                    f"Linha {token_erro['linha']}, "
                    f"Coluna {token_erro['coluna']}\n\n"

                    f"Token inesperado: {atual}\n"
                    f"Lexema encontrado: {lexema_encontrado}\n\n"

                    f"Esperava um dos seguintes:\n"
                    + "\n".join(
                        f"  {e:<15} : "
                        f"{DIC_TOKENS.get(e, 'token desconhecido')}"
                        for e in esperados
                    )
                )

            # Senão, significa que há derivação possível
            producao = tabela[topo][atual]

            # A qual é salva no log
            log.append(f"{topo} -> {' '.join(producao)}")

            
            # Então, cria filhos (derivados do pai), isto é, produção derivada da regra
            # A ser usada tanto para a árvore quanto para a pilha
            filhos = []

            # Se a produção não for vazia:
            if producao != ["ε"]:
                # Para cada símbolo (token ou não-terminal) que derivar:
                for simbolo in producao:
                    # Cria um nó para cada símbolo
                    filho = No(simbolo)
                    # Adiciona-o na lista auxiliar
                    filhos.append(filho)
                    # E adiciona o nó na árvore
                    no_atual.filhos.append(filho)

            # Se a produção for vazia:
            else:
                # Apenas cria o nó
                filho = No("ε")
                # E adiciona-o na árvore
                no_atual.filhos.append(filho)
            # Sem consumir entrada

            # Já para o parser em si, utilizando a produção derivada da regra, empilha a produção invertida na pilha
            # (Sendo o que deriva mais à esquerda na regra o topo, e o mais à direita mais pro fundo)
            
            # Se a produção não derivar para vazio
            if producao != ["ε"]:
                # Para cada símbolo derivado, reverte a ordem de ambos
                for simbolo, filho in zip(reversed(producao), reversed(filhos)):
                    # E sincroniza tanto a pilha do parser
                    pilha.append(simbolo)
                    # Com a pilha da árvore
                    pilha_nos.append(filho)

    # Ao final, tendo sido executado com sucesso, retorna a árvore e o log da execução
    return raiz, log