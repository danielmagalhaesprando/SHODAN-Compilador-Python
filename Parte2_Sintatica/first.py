# Função para determinar se um símbolo é ou não um terminal
def eh_terminal(x, regras):
    # Um símbolo é um terminal se ele não consta como uma "key" das regras da gramática
    # (Ou seja, se ele não é um dos que está do lado esquerdo da gramática)
    return x not in regras and x != "ε"
    # A segunda checagem do ε (símbolo vazio) é necessária para não "consumir" durante o laço do FIRST 


# Retorna o conjunto FIRST do símbolo atual sendo examinado na regra
def first_de_simbolo(simbolo, first, regras):
    # Se este símbolo é um terminal, ele é o próprio FIRST
    if eh_terminal(simbolo, regras):
        return {simbolo}
    # Senão, se ele é um não-terminal, o conjunto FIRST a ser retornado será o conjunto FIRST dele
    return first[simbolo]


# Função principal, que vai criando aos poucos a tabela de FIRST da gramática
def funcao_first(regras):
    # Primeiramente, cria um dicionário de sets, um para cada regra da gramática.
    # Todas inicialmente vazias, mas vão ser preenchidas com o tempo
    first_set = {nt: set() for nt in regras}

    # Variável de controle, se houve mudanças durante o laço
    mudou = True

    # O laço continue enquanto estiverem havendo mudanças no laço
    while mudou:
        # Atribui falso à variável mudou
        # (Se a iteração da função fazer com que hajam mudanças,
        # a variável será colocada em TRUE, e a iteração continuará)
        mudou = False

        # Para cada regra (não-terminal) da gramática,
        for A in regras:
            # Para cada possível produção daquela regra (terminais, não terminais, ou até os dois juntos)
            for prod in regras[A]:

                # Se essa produção for apenas um ε (símbolo vazio)
                if prod == ["ε"]:
                    # Se ε já não faz parte do conjunto de FIRST daquele não-terminal, adicione-o
                    if "ε" not in first_set[A]:
                        # Isso ajuda a evitar duplicações (dois ε no conjunto de FIRST é redundante)
                        first_set[A].add("ε")
                        # Além disso, marca que houve, de fato, uma mudança (afinal, ε não pertencia ao conjunto de FIRST)
                        mudou = True
                    # Continua para a próxima iteração do laço, pois ε não tem símbolos para analisar
                    continue

                # Iterador dos símbolos da produção
                i = 0
                # Assume que toda produção pode gerar símbolo vazio
                add_vazio = True

                # Laço que percorre cada um dos símbolos da produção (terminais ou não)
                while i < len(prod):
                    # Variável do símbolo atual
                    simbolo = prod[i]

                    # Variável que salva o conjunto FIRST desse símbolo atual
                    # (Se esse símbolo for um terminal, apenas retornará ele mesmo)
                    first_simbolo = first_de_simbolo(simbolo, first_set, regras)

                    # Variável apenas para ver se o conjunto FIRST vai mudar
                    antes = len(first_set[A])
                    # Adiciona ao conjunto FIRST do não-terminal atualmente examinado o conjunto FIRST do símbolo atual
                    # (Exceto símbolo vazio, porque ele só entra se todos os símbolos levarem a ele)
                    first_set[A].update(first_simbolo - {"ε"})

                    # Controle de mudança
                    if len(first_set[A]) > antes:
                        mudou = True

                    # Se o símbolo atual não pode gerar ε, para por aqui
                    # Se ela pode, deverá ser analisado o conjunto FIRST do próximo símbolo
                    if "ε" not in first_simbolo:
                        add_vazio = False
                        break

                    # Incrementa para analisar o próximo símbolo
                    i += 1

                # Se todos os símbolos daquela produção podem gerar ε
                if add_vazio:
                    # Caso vazio já não esteja no conjunto FIRST da regra atual, adicione-o então
                    # (Pra evitar duplicação)
                    if "ε" not in first_set[A]:
                        first_set[A].add("ε")
                        # E marque que houve uma mudança, a fim de continuar o laço
                        mudou = True

    # Ao final, retorna a tabela de FIRST completa
    return first_set