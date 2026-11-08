# Dicionário dos estados finais, que realizam a delimitação inicial do token processado
estados_finais = {
    "q1": "ID",
    "q2": "INT",
    "q4": "FLOAT",
    "q6": "STRING",
    "q7": "PAROPEN",
    "q8": "PARCLOSE",
    "q9": "CHAOPEN",
    "q10":"CHACLOSE",
    "q12":"COMENTARIO",
    "q13":"NUMOP",
    "q14":"LOGICOP",
    "q15":"LOGICOP",
    "q16":"RELOP",
    "q17":"RELOP",
    "q18":"RELOP",
    "q19":"ATRIBUICAO",
    "q20":"RELOP",
    "q21":"FINALIZADOR"}

# Grupos de caracteres mapeados para evitar repetições na tabela
NUMOP = {'+', '-', '*', '/', '^'}
LOGICOP = {'&', '|'}
RELOP = {'>', '<'}

# MATRIZ DE TRANSIÇÃO (Tabela Hash O(1))
# Buscas diretas indexadas
MATRIZ_TRANSICAO = {
    "q0":{
        "LETRA": "q1",
        "NUMERO": "q2",
        '"': "q5",
        '(': "q7", ')': "q8", 
        '{': "q9", '}': "q10",
        '%': "q11",
        "NUMOP": "q13",
        "LOGICOP": "q14",
        '!': "q15",
        "RELOP": "q17",
        '=': "q19",
        ';': "q21"},   
    "q1":{
        "LETRA": "q1",
        "NUMERO": "q1"},
    "q2":{
        "NUMERO": "q2",
        '.': "q3"},
    "q3":{
        "NUMERO": "q4"},
    "q4":{
        "NUMERO": "q4"},  
    "q5":{
        "DIFERENTE_ASPAS": "q5",
        '"': "q6"},
    "q11":{
        "DIFERENTE_PORCENTO": "q11",
        '%': "q12"},
    "q15":{
        '=': "q16"},
    "q17":{
        '=': "q18"},
    "q19":{
        '=': "q20"},
}

# Função principal do autômato, que recebe o estado atual, e o caractere lido para determinar a transição
def automato(atual, c):
    # Determinando a classificação do token primeiro:

    # Tratamentos especiais para Strings (q5) e Comentários (q11)
    if atual == "q5":
        if c == "\n":
            return None
        classe = '"' if c == '"' else "DIFERENTE_ASPAS"
    
    elif atual == "q11":
        if c == "\n":
            return None
        classe = '%' if c == '%' else "DIFERENTE_PORCENTO"
    
    # Caso não, então determina a classe com base no caractere
    elif c.isalpha():
        classe = "LETRA"
    elif c.isdigit():
        classe = "NUMERO"
    elif c in NUMOP:
        classe = "NUMOP"
    elif c in LOGICOP:
        classe = "LOGICOP"
    elif c in RELOP:
        classe = "RELOP"
    else:
        classe = c

    # Busca O(1) na tabela: se a transição existir, retorna o novo estado
    if atual in MATRIZ_TRANSICAO and classe in MATRIZ_TRANSICAO[atual]:
        return MATRIZ_TRANSICAO[atual][classe]
        
    return None # Retorna None se a transição for inválida (forçando o lookahead ou erro)
