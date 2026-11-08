#########################################################################################################################################
### CÓDIGO COMPILADOR COMPLETO - LINGUAGEM <SHODAN>                                                                                   ###
#########################################################################################################################################

import sys

from Parte1_Lexical.lexer import lexical
from Parte2_Sintatica.analisador_LL1 import parser_ll1, imprimir_arvore
from Parte3_AST.AST import construir_ast, imprimir_ast
from Parte4_Semantica.analisador_semantico import analisar_semantica
from Parte5_Otimizacao.otimizador_codigo import otimizar_ast
from Parte6_Geracao.gerador_codigo import gerar_codigo

import dis

# Função que valida inteiros
def shodan_int(valor):
    # Verifica se uma conversão implícita de float está sendo feita para int
    if isinstance(valor, float) and not valor.is_integer():
        raise Exception(
            "ERRO DE EXECUCAO:\n"
            "Conversao invalida de float para int."
        )

    return int(valor)

# Função que valida pontos flutuantes
def shodan_float(valor):
    try:
        # Verifica se o valor armazenado no float é complexo
        if isinstance(valor, complex):
            raise Exception(
                "ERRO DE EXECUCAO:\n"
                "Resultado complexo nao suportado."
            )

        return float(valor)
    # Verifica erro de OVERFLOW no float
    except OverflowError:
        raise Exception(
            "ERRO DE EXECUCAO:\n"
            "Numero muito grande para representacao float."
        )

# Função que valida divisões entre números
def shodan_div(a, b):
    try:
        return a / b
    # Verifica erro de DIVISÃO POR ZERO
    except ZeroDivisionError:
        raise Exception(
            "ERRO DE EXECUCAO:\n"
            "Divisao por zero."
        )

# Função que valida potenciações entre números
def shodan_pow(a, b):
    try:
        resultado = a ** b
    # Verifica erro de OVERFLOW
    except OverflowError:
        raise Exception(
            "ERRO DE EXECUCAO:\n"
            "Numero muito grande para representacao."
        )
    # Verifica erro de NÚMERO COMPLEXO
    if isinstance(resultado, complex):
        raise Exception(
            "ERRO DE EXECUCAO:\n"
            "Resultado complexo nao suportado."
        )

    return resultado

# FUNÇÃO PRINCIPAL DO COMPILADOR
#########################################################################################################################################
def main():
    # Lê a entrada do usuário, e a processa como uma string inteira
    entrada = sys.stdin.read()
    
    try:
        # 1 - ANÁLISE LÉXICA
        #################################################################################################################################
        print(f"-----------------------------------------------------------------------")

        lista_tokens = lexical(entrada)
            
        print(f"ANÁLISE LEXICAL CONCLUÍDA!")
        print(f"-----------------------------------------------------------------------")
        
        print(f"LISTA DE TOKENS:\n")
        for token in lista_tokens:
            print(f"{token['nome']}: {token['valor']}")

        # 2 - ANÁLISE SINTÁTICA
        #################################################################################################################################
        print(f"\n-----------------------------------------------------------------------")
        
        arvore, log = parser_ll1(lista_tokens)

        print(f"ANÁLISE SINTÁTICA CONCLUÍDA!")
        print(f"-----------------------------------------------------------------------")

        print(f"LOG DE EXECUÇÃO:\n")
        for l in log:
            print(l)

        print(f"\n-------------------------- ARVORE SINTATICA: --------------------------\n")
        imprimir_arvore(arvore)
    
        # 3 - AST
        #################################################################################################################################
        AST = construir_ast(arvore)

        print(f"\n-------------------------------- AST: ---------------------------------\n")
        imprimir_ast(AST)        
        
        # 4 - ANÁLISE SEMÂNTICA
        #################################################################################################################################
        print(f"\n-----------------------------------------------------------------------")

        tabela = analisar_semantica(AST)

        print(f"ANÁLISE SEMÂNTICA CONCLUÍDA!")
        print(f"-----------------------------------------------------------------------")

        print(f"TABELA DE SIMBOLOS:")
        for nome_variavel, dados in tabela.items():
            print(f"\nNome: {nome_variavel}")
            print(f"Tipo: {dados['tipo']}")
            print(f"Linha: {dados['linha']} ; Coluna: {dados['coluna']}")
        
        # 5 - OTIMIZAÇÃO DE CÓDIGO
        #################################################################################################################################
        AST_otimizada = otimizar_ast(AST)

        print(f"\n--------------------------- AST otimizada: ----------------------------\n")
        imprimir_ast(AST_otimizada)

        # 6 - GERAÇÃO DE CÓDIGO
        #################################################################################################################################
        print(f"\n-----------------------------------------------------------------------")
        
        codigo_python = gerar_codigo(AST_otimizada)
        
        print(f"GERAÇÃO DE CÓDIGO CONCLUÍDA")
        print(f"-----------------------------------------------------------------------")
        
        print(f"CÓDIGO EQUIVALENTE EM PYTHON:\n")
        print(codigo_python)

        # 7 - EXECUÇÃO
        #################################################################################################################################
        print(f"\n-----------------------------------------------------------------------")

        codigo_compilado = compile(codigo_python, "<shodan>", "exec")
        
        # Bytecode do código utilizando a biblioteca dis:
        """
        print("BYTECODE:")
        print("-----------------------------------------------------------------------\n")

        dis.dis(codigo_compilado)

        print("\n-----------------------------------------------------------------------")
        """

        runtime = {
            "shodan_int": shodan_int,
            "shodan_float": shodan_float,
            "shodan_div": shodan_div,
            "shodan_pow": shodan_pow
        }

        exec(codigo_compilado, runtime)

    except Exception as erro:
        print()
        print(erro)
    
if __name__ == "__main__":
    main()
