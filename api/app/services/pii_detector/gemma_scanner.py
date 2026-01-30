import os
import json
from ollama import AsyncClient

class PIIGemmaScanner:
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://ollama:11434", )
        self.model = 'gemma3:4b'
        self.client = AsyncClient(host=self.host)
        
    def prompt(self, text: str):
        return f"""
                Analise se o texto abaixo contém a EXPOSIÇÃO de dados pessoais de uma pessoa física.
                Considere dados pessoais: Nomes próprios de cidadãos, email, telefone, números de celular/whatsapp/zapp, cpf e rg 

                [DIRETRIZES]
                1. SÓ RESPONDA 'Y' se houver o VALOR REAL do dado (Ex: o número do CPF, o endereço do e-mail com @, ou o nome completo).
                2. RESPONDA 'N' se houver apenas a MENÇÃO ao termo (Ex: "mandei um e-mail", "liguei no telefone", "peguei o talão").
                3. RESPONDA 'N' para dados de IMÓVEIS ou PROCESSOS (Matrícula, IPTU, Protocolo 000/000, Inscrição Imobiliária).
                4. RESPONDA 'N' para desabafos, relatos emocionais ou reclamações que não citem nomes próprios ou documentos.
                
                [FORMATO DE SAÍDA]
                - Positivo: "Y [TIPO]"
                - Negativo: "N"
                (Não adicione explicações ou saudações)

                [EXEMPLOS]
                - "Mandei um e-mail para a secretaria." -> N
                - "O telefone dele é 619954324" -> Y Telefone
                - "O e-mail é maria@gmail.com e o nome dela é Maria Silva" -> Y E-mail, Nome
                - "Matrícula do imóvel 4567-RI." -> N
                - "Meu vizinho é barulhento." -> N

                TEXTO:
                "{text}"

                RESPOSTA:
                """

    async def analyze_text(self, text: str):
        response = await self.client.generate(
            model=self.model, 
            prompt=self.prompt(text), 
            options={"temperature": 0}
        )
        
        return response['response'].strip()
