# 🛡️ Sistema de Identificação de PII - CGDF

Bem-vindo à documentação oficial da solução desenvolvida para o Hackathon de Acesso à Informação.

## 🎯 Objetivo
O objetivo deste projeto é automatizar a triagem de pedidos de acesso à informação, identificando dados pessoais (PII) para garantir a proteção da privacidade (LGPD) e a transparência pública.

## 🏗️ Arquitetura da Solução
Nossa solução utiliza um **Modelo Híbrido**:
1. **Microsoft Presidio:** Para detecção veloz de padrões (CPF, Telefone, E-mail).
2. **LLM (DeepSeek/Gemma):** Para análise de contexto semântico, garantindo alta **Sensibilidade (Recall)**.

## 📂 Organização do Projeto
* `api/app/`: Lógica central do Scanner.
* `api/challenge/`: Script de processamento em lote para a banca.
* `api/tests/`: Suite de testes automatizados.

!!! tip "Dica para os Jurados"
    Acesse o menu lateral para ver as instruções detalhadas de **Instalação** e **Execução** do modelo.