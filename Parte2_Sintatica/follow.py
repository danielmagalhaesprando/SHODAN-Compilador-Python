# Função principal, que vai criando aos poucos a tabela de FOLLOW da gramática
def funcao_follow(regras, first_sets, simbolo_inicial):
    # Primeiramente, cria um dicionário de sets, um para cada regra da gramática.
    # Todas inicialmente vazias, mas vão ser preenchidas com o tempo
    follow = {nt: set() for nt in regras}

    # Regra formal: FOLLOW(S) = {$}
    follow[simbolo_inicial].add("$")

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

                # Percorre cada símbolo da produção
                for i in range(len(prod)):
                    B = prod[i]

                    # Se esse símbolo for apenas um ε (símbolo vazio)
                    if B == "ε":
                        # Apenas continua para o próximo símbolo do laço, pois ε não é símbolo da cadeia
                        continue

                    # Se esse símbolo for apenas um terminal
                    if B.startswith("<"):
                        # Apenas continua para o próximo símbolo do laço, pois FOLLOW só existe para não-terminais
                        continue

                    # Controle de mudança: guarda tamanho antes de modificar
                    antes = len(follow[B])

                    # Se o símbolo atual for o último símbolo
                    if i == len(prod) - 1:
                        # Adicionar o FOLLOW da regra atual ao FOLLOW deste símbolo não-terminal
                        follow[B].update(follow[A])

                    # Se o símbolo atual não for o último símbolo
                    else:
                        # Agora irá checar todos os casos não simples
                        j = i + 1

                        # Percorre todos os símbolos após B
                        while j < len(prod):
                            simbolo = prod[j]

                            # Se este símbolo for um terminal,
                            if simbolo.startswith("<"):
                                # adicione-o ao FOLLOW do não-terminal anterior
                                follow[B].add(simbolo)
                                # e quebra, porque, como é um terminal, não há mais o que analisar
                                break

                            # Este símbolo que vem após
                            first_simbolo = first_sets[simbolo]

                            # Adicions todos os FIRST dele ao FOLLOW de B (todos os terminais que podem ser o seu primeiro)
                            follow[B].update(first_simbolo - {"ε"})

                            # Se ele não tem ε, então para manualmente
                            if "ε" not in first_simbolo:
                                break

                            j += 1

                        # Se todos à direita geram ε
                        if j == len(prod):
                            follow[B].update(follow[A])

                    if len(follow[B]) > antes:
                        mudou = True

    return follow