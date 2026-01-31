# Guia de Instalação do Sistema

Antes de iniciar, é necessário garantir que o ambiente possua Docker e Docker Compose instalados. Recomenda-se Docker versão 20 ou superior e Docker Compose v2. Não é necessário instalar Python, PostgreSQL ou RabbitMQ localmente, pois todos esses componentes são executados em containers.

O primeiro passo é preparar o arquivo de variáveis de ambiente. No repositório do projeto existe um arquivo `.env.example`, que deve ser copiado para `.env`. Esse arquivo centraliza todas as configurações necessárias para o funcionamento do sistema, incluindo credenciais de banco de dados, mensageria, integração com webhook externo e, opcionalmente, configurações de LLM.

As variáveis relacionadas ao PostgreSQL permitem duas abordagens distintas. Caso você queira subir uma instância dedicada apenas para este sistema, basta manter as variáveis `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB` conforme o exemplo. A URL de conexão (`DATABASE_URL`) já está preparada para apontar para o container do PostgreSQL definido no Docker Compose. Caso você já possua um banco externo, basta sobrescrever a variável `DATABASE_URL` com a string de conexão adequada, podendo inclusive remover o serviço de PostgreSQL do compose se desejar.

De forma semelhante, o RabbitMQ também pode ser utilizado de duas maneiras. Por padrão, o Docker Compose sobe uma instância local do RabbitMQ, utilizando as credenciais definidas em `RABBIT_USER` e `RABBIT_PASSWORD`. A variável `RABBIT_URL` aponta automaticamente para esse container. Em ambientes onde já existe um broker disponível, basta alterar essa URL para o endereço externo e, se necessário, remover o serviço `rabbitmq` do compose.

Outro ponto importante do arquivo `.env` é a configuração do webhook. A variável `WEBHOOK_URL` define para onde o dispatcher enviará os resultados do processamento. Em ambiente local, é comum utilizar `http://host.docker.internal` para alcançar um serviço rodando fora do Docker, como um servidor Express em Node.js. Também é possível configurar um segredo opcional para o webhook, que será enviado como header HTTP, aumentando a segurança da integração.

O sistema também suporta, de forma opcional, um fallback para LLM. Quando habilitado, caso o mecanismo principal de detecção não encontre dados sensíveis, uma LLM pode ser utilizada como segunda camada de análise. Essa funcionalidade é controlada pela variável `LLM_FALLBACK`. Caso seja ativada, é necessário informar o modelo, a URL base da API e a chave de autenticação.

Com o arquivo `.env` devidamente configurado, o próximo passo é subir os containers. A partir da raiz do projeto, basta executar o comando:

```
docker compose up --build
```

Esse comando irá construir as imagens da API, do worker e do dispatcher, além de iniciar os containers do PostgreSQL e do RabbitMQ. Durante a primeira execução, o processo pode levar alguns minutos devido ao build das imagens e à inicialização dos serviços.

Após a subida dos containers, a API REST ficará disponível, por padrão, na porta 8000 do host. Nesse ponto, já é possível enviar requisições HTTP para o endpoint de criação de processamento, enviando um texto para análise. A resposta da API será imediata, retornando um status de sucesso, enquanto o processamento ocorrerá de forma assíncrona em background.

Para fins de observabilidade e depuração, o RabbitMQ Management Plugin fica acessível na porta 15672, permitindo acompanhar filas, consumidores e taxa de mensagens. Os logs de cada serviço podem ser acompanhados diretamente pelo Docker Compose, facilitando a identificação de problemas durante a instalação ou execução.

Caso seja necessário interromper o sistema, basta utilizar `docker compose down`. Os dados do PostgreSQL e do RabbitMQ são persistidos em volumes Docker, o que garante que informações não sejam perdidas entre reinicializações, a menos que os volumes sejam removidos explicitamente.
