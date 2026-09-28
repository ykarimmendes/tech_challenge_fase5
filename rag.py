from pathlib import Path
import re
import unicodedata

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==================================================
# CAMINHO DA BASE
# ==================================================

CAMINHO_BASE = (
    Path(__file__).parent
    / "data"
    / "conhecimento_imobiliario.md"
)


# ==================================================
# NORMALIZAR TEXTO
# ==================================================

def normalizar_texto(texto):

    texto = texto.casefold()

    texto = "".join(
        c
        for c in unicodedata.normalize(
            "NFD",
            texto
        )
        if unicodedata.category(c) != "Mn"
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ==================================================
# CARREGAR BASE
# ==================================================

def carregar_base():

    if not CAMINHO_BASE.exists():

        raise FileNotFoundError(
            "Base de conhecimento não encontrada: "
            f"{CAMINHO_BASE}"
        )

    return CAMINHO_BASE.read_text(
        encoding="utf-8"
    )


# ==================================================
# DIVIDIR EM TRECHOS
# ==================================================

def dividir_em_trechos(texto):

    """
    Divide o Markdown usando títulos de nível 2.

    Cada seção funciona como um documento
    independente para recuperação.
    """

    partes = re.split(
        r"\n(?=## )",
        texto
    )

    trechos = []

    for parte in partes:

        parte = parte.strip()

        if not parte:
            continue

        if parte.startswith(
            "# Base de Conhecimento"
        ):

            continue

        trechos.append(
            parte
        )

    return trechos


# ==================================================
# EXTRAIR TÍTULO
# ==================================================

def extrair_titulo(trecho):

    linhas = trecho.splitlines()

    if not linhas:

        return "Sem título"

    titulo = linhas[0]

    titulo = titulo.replace(
        "##",
        ""
    ).strip()

    return titulo


# ==================================================
# BUSCAR CONTEXTO
# ==================================================

def buscar_contexto(
    pergunta,
    top_k=3,
    limite_similaridade=0.08
):

    """
    Recupera os trechos mais relevantes
    utilizando TF-IDF + similaridade de cosseno.
    """

    base = carregar_base()

    trechos = dividir_em_trechos(
        base
    )

    if not trechos:

        return []


    documentos_normalizados = [
        normalizar_texto(
            trecho
        )
        for trecho in trechos
    ]


    pergunta_normalizada = (
        normalizar_texto(
            pergunta
        )
    )


    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2)
    )


    matriz = vectorizer.fit_transform(
        documentos_normalizados
        + [
            pergunta_normalizada
        ]
    )


    vetor_pergunta = matriz[
        -1
    ]


    matriz_documentos = matriz[
        :-1
    ]


    similaridades = (
        cosine_similarity(
            vetor_pergunta,
            matriz_documentos
        )[0]
    )


    indices = (
        similaridades
        .argsort()[::-1]
    )


    resultados = []


    for indice in indices:

        score = float(
            similaridades[
                indice
            ]
        )


        if score < limite_similaridade:
            continue


        trecho = trechos[
            indice
        ]


        resultados.append(
            {
                "titulo":
                    extrair_titulo(
                        trecho
                    ),

                "conteudo":
                    trecho,

                "score":
                    round(
                        score,
                        4
                    )
            }
        )


        if len(
            resultados
        ) >= top_k:

            break


    return resultados


# ==================================================
# FORMATAR CONTEXTO PARA O LLM
# ==================================================

def formatar_contexto(
    resultados
):

    if not resultados:

        return ""


    blocos = []


    for item in resultados:

        blocos.append(
            item[
                "conteudo"
            ]
        )


    return "\n\n---\n\n".join(
        blocos
    )


# ==================================================
# TESTE LOCAL
# ==================================================

if __name__ == "__main__":

    pergunta = input(
        "Pergunta: "
    )


    resultados = buscar_contexto(
        pergunta
    )


    if not resultados:

        print(
            "\nNenhuma informação relevante encontrada."
        )

    else:

        print(
            "\nTrechos recuperados:\n"
        )


        for item in resultados:

            print(
                f"Título: {item['titulo']}"
            )

            print(
                f"Similaridade: {item['score']}"
            )

            print(
                item[
                    "conteudo"
                ]
            )

            print(
                "\n"
                + "-" * 60
                + "\n"
            )