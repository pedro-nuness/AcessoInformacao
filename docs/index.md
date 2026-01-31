# Identificação de PII - Hackathon CGDF

Bem-vindo à documentação oficial da solução desenvolvida para o *1º Hackathon em Controle Social: Desafio Participa DF*.

## Contexto do Projeto
Este projeto foi concebido para a **Categoria Acesso à Informação**. O desafio proposto pela CGDF consiste em desenvolver modelos capazes de identificar automaticamente pedidos de acesso à informação que contenham dados pessoais, garantindo que manifestações que deveriam ser restritas não sejam classificadas indevidamente como públicas.

!!! abstract "Escopo de Dados Pessoais (Edital)"
    De acordo com as diretrizes do edital para este Hackathon, o modelo foi configurado para identificar especificamente as seguintes entidades como dados pessoais restritos:
    **RG, CPF, Nome, Telefone e E-mail.**

## Tecnologias Utilizadas
* **Linguagem:** Python 3.10+
* **IA & NLP:** Microsoft Presidio, Spacy (pt_core_news_lg).
* **LLM:** DeepSeek para análise semântica de contexto.
* **Processamento:** Pandas e TQDM para gestão de grandes volumes de dados (batch).

## Contribuidores

<center>
    <table>
    <tr>
        <td align="center">
        <a href="https://github.com/danielle-soaress">
            <img src="https://github.com/danielle-soaress.png" width="190" style="border-radius: 50%;" alt="Danielle Soares"/>
            <br/><sub><b>Danielle Soares</b></sub>
        </a>
        </td>
        <td align="center">
        <a href="https://github.com/pedro-nuness">
            <img src="https://github.com/pedro-nuness.png" width="190" style="border-radius: 50%;" alt="Pedro Henrique Nunes"/>
            <br/><sub><b>Pedro Henrique Nunes</b></sub>
        </a>
        </td>
    </table>
</center>