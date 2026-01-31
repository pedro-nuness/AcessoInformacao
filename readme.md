# Sistema de Classificação de Texto Sensível

Este projeto foi desenvolvido no contexto de um **hackathon do Participa DF**, com o objetivo de propor uma solução técnica para identificação automatizada de conteúdos textuais que contenham informações sensíveis. A aplicação foi pensada para cenários reais de uso governamental e institucional, onde é necessário analisar grandes volumes de texto de forma confiável, escalável e auditável.

O sistema recebe textos por meio de uma API REST e realiza a classificação de forma assíncrona, indicando se o conteúdo contém ou não dados sensíveis. Todo o fluxo foi desenhado para priorizar desacoplamento, resiliência e escalabilidade, permitindo operação estável mesmo sob alta carga.

## Visão Geral da Solução

A arquitetura adota um modelo orientado a eventos. A API atua apenas como porta de entrada, persistindo os dados e publicando eventos em uma fila de mensagens. O processamento pesado ocorre em serviços separados, consumindo essas mensagens de forma assíncrona. Essa abordagem garante baixa latência na resposta inicial ao cliente e maior tolerância a picos de requisição.

O sistema mantém o estado completo do processamento em banco de dados, possibilitando rastreabilidade, auditoria e integração com sistemas externos. Ao final do processamento, os resultados podem ser enviados automaticamente para serviços terceiros por meio de webhooks, com mecanismos de proteção contra falhas externas.

## Principais Características

* API REST para submissão de textos
* Processamento assíncrono orientado a eventos
* Persistência de estado e resultados
* Integração via webhook com sistemas externos
* Mecanismos de resiliência, como circuit breaker
* Arquitetura preparada para escalabilidade horizontal
* Suporte opcional a fallback com LLM

## Componentes do Sistema

A solução é composta por uma API responsável pela entrada dos dados, um serviço de processamento que realiza a análise de sensibilidade do texto, um dispatcher que notifica sistemas externos e componentes de infraestrutura como banco de dados PostgreSQL e mensageria RabbitMQ. Todos os serviços são executados em containers Docker e orquestrados via Docker Compose.

## Contexto do Hackathon

O projeto foi desenvolvido como parte de um hackathon promovido pelo **Participa DF**, com foco em inovação, uso responsável de tecnologia e melhoria de processos relacionados à análise e tratamento de informações textuais. As decisões arquiteturais priorizam simplicidade operacional, clareza de responsabilidades e aderência a cenários reais de produção.

## Considerações Finais

Este repositório apresenta uma prova de conceito funcional, com arquitetura sólida e orientada a boas práticas de engenharia de software. O projeto pode ser evoluído para uso em produção com ajustes pontuais de infraestrutura, segurança e observabilidade, mantendo a base arquitetural já estabelecida.

A documentação complementar descreve a arquitetura detalhada, os resultados de testes de carga e o processo de instalação e execução do sistema.
