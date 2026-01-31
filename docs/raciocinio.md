# Raciocínio Técnico

Esta página detalha a fundamentação lógica e as escolhas arquiteturais que sustentam a robustez da solução de detecção de **PII (Personally Identifiable Information)**.

## 1. Objetivo

Identificar automaticamente pedidos de acesso à informação que contêm exposição de dados pessoais — especificamente: **Nome, CPF, RG, Telefone e E-mail** — para impedir a publicação indevida de manifestações sensíveis.

## 2. O Problema Central

O processamento de manifestações públicas enfrenta o desafio do volume e da variabilidade de formatos. A solução precisa equilibrar duas métricas fundamentais:

* **Precisão:** Não bloquear textos legítimos/públicos por erro do modelo.
* **Sensibilidade (Recall):** Não permitir o vazamento de nenhum dado pessoal real.

## 3. Lógica do Fluxo de Dados

A solução foi desenhada para ser escalável, utilizando um processamento assíncrono:

1. **Entrada:** As mensagens com texto entram em uma fila de processamento (**RabbitMQ**).
2. **Consumo:** O Worker (`app/services/worker.py`) consome a fila e dispara o método `analyze_text`.
3. **Análise Híbrida (`analyze_text`):**
* **Camada 1 (PresidioScanner):** Executa detecção baseada em padrões e reconhecedores customizados.
* **Camada 2 (LLMScanner - Fallback):** Se a primeira camada for inconclusiva, uma LLM com prompt restrito decide entre `PRIVATE` ou `PUBLIC`.
4. **Saída:** Os resultados são gravados e despachados via **webhook**, contando com mecanismos de *retry* e *circuit-breaker*.

## 4. Diferenciais Estratégicos

### Validação de Documentos Reais (CPF/CNPJ)

Diferente de soluções baseadas apenas em Regex, nosso `PresidioScanner` integra reconhecedores customizados que utilizam a biblioteca `validate_docbr`.

* **CPFs Válidos:** Somente sequências numéricas que passam no teste do dígito verificador são marcadas como PII.
* **CPFs Inválidos:** Números aleatórios que não correspondem a documentos reais são ignorados, reduzindo drasticamente os Falsos Positivos.

### O Papel da LLM Restrita

A LLM entra em cena para capturar exposições que não seguem formatos rígidos, como:

* Nomes completos em contextos variados.
* Endereços e referências pessoais implícitas.

> **Segurança do Prompt:** O modelo responde `Y [TIPO]` ou `N`, minimizando alucinações e garantindo uma decisão binária clara.

## 5. Riscos e Mitigações

| Risco | Estratégia de Mitigação |
| --- | --- |
| **Falsos Positivos (Regex)** | Validação matemática de documentos e análise de palavras-chave contextuais. |
| **Falsos Negativos (LLM)** | Prompt rígido e enviesado para a segurança (na dúvida, classifica como `PRIVATE`). |
| **Indisponibilidade de API** | Sistema de logs de auditoria e fila de retentativa automática. |


