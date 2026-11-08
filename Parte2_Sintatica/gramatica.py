# Regras da gramática:
regras = {
    "[PROGRAMA_GRAMATICA]": [
        ["[PROGRAMA]"]
    ],

    "[PROGRAMA]": [
        ["[DECLARACAO]", "[PROGRAMA]"],
        ["[ATRIBUICAO]", "[PROGRAMA]"],
        ["[IMPRESSAO]", "[PROGRAMA]"],
        ["[IF-ELSE]", "[PROGRAMA]"],
        ["[WHILE]", "[PROGRAMA]"],
        ["ε"]
    ],

    "[DECLARACAO]": [
        ["<TIPO>", "<ID>", "<ATRIBUICAO>", "[EXPRESSAO]", "<FINALIZADOR>"]
    ],

    "[ATRIBUICAO]": [
        ["<ID>", "<ATRIBUICAO>", "[EXPRESSAO]", "<FINALIZADOR>"]
    ],

    "[IMPRESSAO]": [
        ["<PRINT>", "<PAROPEN>", "[EXPRESSAO]", "<PARCLOSE>", "<FINALIZADOR>"]
    ],

    "[WHILE]": [
        ["<WHILE>", "<PAROPEN>", "[EXPRESSAO]", "<PARCLOSE>", "[THEN]"]
    ],

    "[IF-ELSE]": [
        ["[IF]", "[ELSEIFS]", "[ELSE]"]
    ],

    "[IF]": [
        ["<IF>", "<PAROPEN>", "[EXPRESSAO]", "<PARCLOSE>", "[THEN]"]
    ],

    "[ELSEIFS]": [
        ["[ELSEIF]", "[ELSEIFS]"],
        ["ε"]
    ],

    "[ELSEIF]": [
        ["<ELSEIF>", "<PAROPEN>", "[EXPRESSAO]", "<PARCLOSE>", "[THEN]"]
    ],

    "[ELSE]": [
        ["<ELSE>", "[THEN]"],
        ["ε"]
    ],

    "[THEN]": [
        ["<CHAOPEN>", "[PROGRAMA]", "<CHACLOSE>"]
    ],

    "[EXPRESSAO]": [
        ["[EXPR_OR]"]
    ],

    "[EXPR_OR]": [
        ["[EXPR_AND]", "[EXPR_OR']"]
    ],

    "[EXPR_OR']": [
        ["<LOGIC_OR>", "[EXPR_AND]", "[EXPR_OR']"],
        ["ε"]
    ],

    "[EXPR_AND]": [
        ["[EXPR_RELACIONAL]", "[EXPR_AND']"]
    ],

    "[EXPR_AND']": [
        ["<LOGIC_AND>", "[EXPR_RELACIONAL]", "[EXPR_AND']"],
        ["ε"]
    ],

    "[EXPR_RELACIONAL]": [
        ["[EXPR_SOMASUB]", "[EXPR_RELACIONAL']"]
    ],

    "[EXPR_RELACIONAL']": [
        ["<RELOP>", "[EXPR_SOMASUB]"],
        ["ε"]
    ],

    "[EXPR_SOMASUB]": [
        ["[EXPR_MULDIV]", "[EXPR_SOMASUB']"]
    ],

    "[EXPR_SOMASUB']": [
        ["<NUMOP_+->", "[EXPR_MULDIV]", "[EXPR_SOMASUB']"],
        ["ε"]
    ],

    "[EXPR_MULDIV]": [
        ["[EXPR_POT]", "[EXPR_MULDIV']"]
    ],

    "[EXPR_MULDIV']": [
        ["<NUMOP_*/>", "[EXPR_POT]", "[EXPR_MULDIV']"],
        ["ε"]
    ],

    "[EXPR_POT]": [
        ["[EXPR_UNARIO]", "[EXPR_POT']"]
    ],

    "[EXPR_POT']": [
        ["<NUMOP_^>", "[EXPR_POT]"],
        ["ε"]
    ],

    "[EXPR_UNARIO]": [
        ["<LOGIC_NOT>", "[EXPR_UNARIO]"],
        ["<NUMOP_+->", "[EXPR_UNARIO]"],
        ["[EXPR_PRIMARIO]"]
    ],

    "[EXPR_PRIMARIO]": [
        ["<ID>"],
        ["[LITERAL]"],
        ["<PAROPEN>", "[EXPRESSAO]", "<PARCLOSE>"]
    ],

    "[LITERAL]": [
        ["<INT>"],
        ["<FLOAT>"],
        ["<STRING>"]
    ]
}

SIMBOLO_INICIAL = "[PROGRAMA_GRAMATICA]"