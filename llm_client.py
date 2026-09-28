"""Cliente da API local do Ollama. Nenhuma credencial necessária."""

import json
import os
from urllib.error import URLError
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, model=None, base_url=None, timeout=180):
        self.model = model or os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5:3b"
        )

        self.base_url = (
            base_url
            or os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434"
            )
        ).rstrip("/")

        self.timeout = timeout


    # ==========================================
    # EXTRAÇÃO ESTRUTURADA
    # ==========================================

    def extrair(self, mensagens, schema):

        payload = {
            "model": self.model,
            "messages": mensagens,
            "format": schema,
            "stream": False,
            "options": {
                "temperature": 0
            }
        }

        request = Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:

            with urlopen(
                request,
                timeout=self.timeout
            ) as response:

                result = json.load(
                    response
                )

            if result.get(
                "done"
            ) is not True:

                raise ValueError(
                    "Resposta incompleta"
                )

            return json.loads(
                result[
                    "message"
                ][
                    "content"
                ]
            )

        except (
            URLError,
            TimeoutError,
            OSError,
            ValueError,
            KeyError,
            TypeError
        ) as exc:

            raise LLMError(
                "Ollama indisponível ou resposta inválida"
            ) from exc


    # ==========================================
    # RESPOSTA COM CONTEXTO - RAG
    # ==========================================

    def responder_com_contexto(
        self,
        pergunta,
        contexto
    ):

        mensagens = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente imobiliário. "
                    "Responda utilizando apenas as informações "
                    "presentes no contexto fornecido. "
                    "Não invente informações. "
                    "Se o contexto não contiver informação suficiente "
                    "para responder, diga: "
                    "'Não encontrei essa informação na base de conhecimento.' "
                    "Responda de forma clara, objetiva e natural."
                )
            },
            {
                "role": "user",
                "content": (
                    f"CONTEXTO:\n{contexto}\n\n"
                    f"PERGUNTA:\n{pergunta}"
                )
            }
        ]

        payload = {
            "model": self.model,
            "messages": mensagens,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        request = Request(
            self.base_url + "/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:

            with urlopen(
                request,
                timeout=self.timeout
            ) as response:

                result = json.load(
                    response
                )

            if result.get(
                "done"
            ) is not True:

                raise ValueError(
                    "Resposta incompleta"
                )

            return result[
                "message"
            ][
                "content"
            ].strip()

        except (
            URLError,
            TimeoutError,
            OSError,
            ValueError,
            KeyError,
            TypeError
        ) as exc:

            raise LLMError(
                "Ollama indisponível ou resposta inválida"
            ) from exc