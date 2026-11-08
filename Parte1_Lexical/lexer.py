#########################################################################################################################################
### CÓDIGO ANALISADOR LEXICAL - LINGUAGEM <SHODAN>                                                                                       ###
#########################################################################################################################################

from .automato import estados_finais, automato


# Dicionário de erros léxicos, a ser usada para determinar o motivo de um erro
DIC_ERROS_LEXICOS = {
    "q3": "float incompleto",
    "q5": "string não fechada",
    "q11": "comentario não fechado"
}

# Dicionário de reatribuições
REMAP_TOKENS = {
    "int": "<TIPO>", "float": "<TIPO>", "string": "<TIPO>",
    "print": "<PRINT>",
    "while": "<WHILE>",
    "if": "<IF>", "elseif": "<ELSEIF>", "else": "<ELSE>",
    "|": "<LOGIC_OR>", "&": "<LOGIC_AND>", "!": "<LOGIC_NOT>",
    "+": "<NUMOP_+->", "-": "<NUMOP_+->",
    "*": "<NUMOP_*/>", "/": "<NUMOP_*/>",
    "^": "<NUMOP_^>"
}

# PROCESSAMENTO PRINCIPAL - ANÁLISE LEXICAL:
#########################################################################################################################################
# Recebe como entrada o código do usuário
def lexical(entrada):
    atual = "q0"            # variável do estado atual
    tokens = []             # lista contendo todos tokens registrados durante a leitura
    token = ""              # palavra que está sendo lida no momento
    linha = 1               # linha atual (inicia em 1)
    coluna = 1              # coluna atual (inicia em 1 também)
    linha_inicio = linha    # linha de início do token atual
    coluna_inicio = coluna  # coluna de início do token atual

    i = 0
    # O analisador funciona lendo caractere por caractere da string de entrada,
    # e processando-a no autômato, consumindo um caractere por transição
    while i < len(entrada):
        c = entrada[i]
 
        # Quando ler um espaço, ou quebra de linha, ou tabulação, etc, acabou de ler uma palavra
        if c.isspace() and atual not in {"q5", "q11"}:
            # Se essa palavra é válida (está atualmente em um estado final), salva-a em um token e recomeça o processo
            if atual in estados_finais:
                tokens.append({
                    "nome": "<" + estados_finais[atual] + ">",
                    "valor": token,
                    "linha": linha_inicio,
                    "coluna": coluna_inicio})
                atual = "q0"
                token = ""
                i += 1
                
                # Atualização de posição
                if c == "\n":
                    linha += 1
                    coluna = 1
                else:
                    coluna += 1
                
                continue
 
            # No caso específico que o espaço/quebra de linha é a primeira coisa que ele lê (como no caso de dois espaços entre palavras),
            # apenas ignora o espaço irrelevante e continua o processamento
            elif atual == "q0":
                i += 1

                # Atualização de posição
                if c == "\n":
                    linha += 1
                    coluna = 1
                else:
                    coluna += 1
                
                continue
 
            # No caso da palavra lida antes do espaço/quebra de linha não ser válida, isto é, o autômato não está em um estado final,
            # finaliza a análise com ERRO LÉXICO e comunica a main
            else:
                raise Exception(
                    f"ERRO LEXICO:\n"
                    f"Linha {linha_inicio}, Coluna {coluna_inicio}\n"
                    f"{DIC_ERROS_LEXICOS.get(atual,"token invalido antes de espaço")}"
                )
            
        # Consulta direta O(1) no autômato
        proximo = automato(atual, c)

        if proximo is not None:
            # Guarda a coordenada inicial exata de onde o token começou quando sai de q0
            if atual == "q0":
                linha_inicio = linha
                coluna_inicio = coluna
            atual = proximo
            token = token + c
 
        # Caso leia um caractere que provenha uma transição inválida no autômato
        else:
            # Para o caso de a palavra que leu até aqui ser válida, salva ela em um token
            # E tenta ver se o caractere provê uma transição válida por si só
            if atual in estados_finais:
                tokens.append({
                    "nome": "<" + estados_finais[atual] + ">",
                    "valor": token,
                    "linha": linha_inicio,
                    "coluna": coluna_inicio})
                atual = "q0"
                token = ""
                continue # reprocessa o mesmo caractere, sem consumí-lo, para ver se é válido a partir de q0
 
            # Se mesmo assim não for possível, significa um ERRO LÉXICO
            else:
                raise Exception(
                    f"ERRO LEXICO:\n"
                    f"Linha {linha}, Coluna {coluna}\n"
                    f"{DIC_ERROS_LEXICOS.get(atual,f"caractere invalido '{c}'")}"
                )

        i += 1

        # Atualização de posição
        if c == "\n":
            linha += 1
            coluna = 1
        else:
            coluna += 1

    # Ao final da análise do autômato, quando toda a string houver sido processada
    # A última palavra não foi analisada, pois o WHILE quebrou antes

    # Então, caso a última palavra seja uma palavra válida (está em um estado final), salva ela no token
    if atual in estados_finais:
        tokens.append({
            "nome": "<" + estados_finais[atual] + ">",
            "valor": token,
            "linha": linha_inicio,
            "coluna": coluna_inicio})
 
    # Caso contrário, significa um ERRO LÉXICO
    elif atual != "q0":
        raise Exception(
        f"ERRO LEXICO:\n"
        f"Linha {linha_inicio}, Coluna {coluna_inicio}\n"
        f"{DIC_ERROS_LEXICOS.get(atual,"token invalido no final da entrada")}"
    )
    
    # PÓS-PROCESSAMENTO:
    #####################################################################################################################################

    # Por fim, ocorre uma reatribuição, de palavras reservadas
    # Realizando uma ponte entre a análise lexical e a análise sintática

    # Reatribuição de palavras reservadas utilizando busca hash
    for t in tokens:
        if t["valor"] in REMAP_TOKENS:
            t["nome"] = REMAP_TOKENS[t["valor"]]
    
    #####################################################################################################################################

    # Além disso, remove aspas simples e duplas duplicadas (string de string) de uma STRING

    for t in tokens:
        if t["nome"] == "<STRING>":
            t["valor"] = t["valor"][1:-1]

    #####################################################################################################################################

    # Além disso, remove todos os tokens de <COMENTARIO> ao final da análise lexical, não os passando adiante
    
    tokens_filtrados = [t for t in tokens if t["nome"] != "<COMENTARIO>"]

    # E, por fim, tendo sido executado com sucesso, retorna a lista de tokens produzida a partir da entrada
    return tokens_filtrados
