from .gramatica import regras, SIMBOLO_INICIAL

from .first import funcao_first
from .follow import funcao_follow


# Função auxiliar: FIRST de uma sequência
def first_sequencia(sequencia, first_set):
    resultado = set()

    # Caso especial: ε
    if sequencia == ["ε"]:
        resultado.add("ε")
        return resultado

    for simbolo in sequencia:
        # Terminal
        if simbolo.startswith("<"):
            resultado.add(simbolo)
            return resultado

        # Não-terminal
        resultado.update(first_set[simbolo] - {"ε"})

        # Se não possui ε, encerra
        if "ε" not in first_set[simbolo]:
            return resultado

    # Todos possuem ε
    resultado.add("ε")

    return resultado


# Construção da tabela
def construir_tabela():
    # FIRST e FOLLOW
    first_set = funcao_first(regras)
    follow_set = funcao_follow(regras, first_set, SIMBOLO_INICIAL)

    # Tabela de parsing, inicialmente vazia
    tabela = {}
    for nao_terminal in regras:
        tabela[nao_terminal] = {}


    # Construção da tabela de parsing:

    # Para cada uma das regras da gramática:
    for A in regras:
        # Avalia todas as produções dessa regra
        producoes = regras[A]
        # E para cada uma dessas produções:
        for producao in producoes:
            # Encontra o conjunto FIRST dessa produção
            primeiros = first_sequencia(producao, first_set)

            # Com o conjunto FIRST dessa produção, avalia para qual regra (1 apenas) deve derivar se ver determinado terminal desse conjunto
            # Exceto o ε. O ε (vazio) no FIRST significa que a produção inteira pode ser vazia, fazendo-se necessário olhar o FOLLOW (depois)
            for terminal in primeiros - {"ε"}:
                # Detecta conflito LL(1)
                if terminal in tabela[A]:
                    raise Exception(
                        "CONFLITO LL(1) DETECTADO:\n"
                        f"Nao-terminal: {A}\n"
                        f"Token conflitante: {terminal}\n"
                        "Duas producoes diferentes tentaram ocupar a mesma celula da tabela LL(1):\n"
                        f"Regra já existente na tabela: {tabela[A][terminal]}\n"
                        f"Nova regra com mesmo token: {producao}\n"
                        "A gramatica deixou de ser deterministica para 1 token de lookahead."
                    )

                # Se não houver conflito, forma na tabela a linha-coluna determinística da produção a ser seguida se ler aquele token
                tabela[A][terminal] = producao

            # Se o ε pertence ao conjunto FIRST daquela produção (isto é, a produção inteira pode ser vazia)
            # Então usa-se o conjunto FOLLOW para averiguar qual token pode seguir aquela produção
            if "ε" in primeiros:
                # Com o conjunto FOLLOW dessa produção, avalia para qual regra (1 apenas) deve derivar se ver determinado terminal desse conjunto
                for terminal in follow_set[A]:
                    # Detecta conflito LL(1)
                    if terminal in tabela[A]:
                        raise Exception(
                            "CONFLITO LL(1) DETECTADO:\n"
                            f"Nao-terminal: {A}\n"
                            f"Token conflitante: {terminal}\n"
                            "Duas producoes diferentes tentaram ocupar a mesma celula da tabela LL(1):\n"
                            f"Regra já existente na tabela: {tabela[A][terminal]}\n"
                            f"Nova regra com mesmo token: {producao}\n"
                            "A gramatica deixou de ser deterministica para 1 token de lookahead."
                        )

                    # Se não houver conflito, forma na tabela a linha-coluna determinística da produção a ser seguida se ler aquele token
                    tabela[A][terminal] = producao
    
    return tabela, SIMBOLO_INICIAL
