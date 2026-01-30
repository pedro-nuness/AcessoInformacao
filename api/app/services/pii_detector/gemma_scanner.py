import os
import json
from ollama import AsyncClient

class PIIGemmaScanner:
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://ollama:11434", )
        self.client = AsyncClient(host=self.host, timeout=60.0)
        self.model = 'gemma3:4b'

    async def analyze_text(self, text: str):
        prompt = f"""
                Objetivo: Identificar apenas dados de pessoas naturais (Nome, CPF, RG, Telefone, E-mail).

                REGRAS:
                1. NÃO classifique como PII: Números de processos, endereços, nomes de órgãos públicos ou locais públicos.
                2. Classifique como 'Y' se houver dados privados de cidadãos.
                3. Classifique como 'N' se o texto for puramente administrativo.

                RESPOSTA:
                'Y' + tipos encontrados OU 'N' + 'Texto Seguro'

                TEXTO: {text}
                """
        
        response = await self.client.generate(
            model=self.model, 
            prompt=prompt, 
            options={"temperature": 0}
        )
        return response['response'].strip()