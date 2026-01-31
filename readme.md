# Participa DF — Identificação de PII (Hackathon) 🔐

Solução desenvolvida para o **1º Hackathon em Controle Social - Desafio Participa DF**. O objetivo é identificar automaticamente pedidos de acesso à informação que contenham *exposição de dados pessoais* (PII) — e impedir que manifestações sensíveis sejam classificadas como públicas.

---

## 📚 Documentação
A documentação detalhada está em `docs/`:
- `docs/index.md` — visão geral do projeto
- `docs/arquitetura.md` — decisões arquiteturais e resultados de carga
- `docs/instalacao.md` — guia de instalação e utilização com Docker
- `docs/raciocinio.md` — raciocínio técnico por trás das escolhas

---

## 🧭 Visão geral da solução
- Entrada: API (FastAPI) que aceita textos e responde rapidamente (202 Accepted) enquanto o processamento ocorre assíncronamente.
- Processamento: mensagens enfileiradas (RabbitMQ) e consumidas por workers que aplicam os detectores de PII.
- Detectores:
  - **Presidio** com reconhecedores customizados (CPF, e‑mail, telefone, CNPJ, etc.) — primeira linha de defesa (detecção determinística + validação).
  - **LLM (fallback controlado)** — quando o Presidio não encontra entidades, o LLM responde `Y [TIPO]` / `N` para decidir exposição semântica.
- Dispatcher: monitora o banco por registros finalizados e envia resultados a um webhook com retry e circuito de proteção.

---

## ⚙️ Requisitos
- Docker & Docker Compose (recomendado para demo/produção)
- Python 3.10+ (para execução local de desenvolvimento)
- SpaCy pt model (`pt_core_news_lg`) se rodar localmente

---

## 🚀 Instalação rápida (Docker Compose)
1. Copie `.env.example` para `.env` e ajuste variáveis (DB, RabbitMQ, WEBHOOK, LLM se necessário).
2. Suba os serviços:

```bash
docker compose up --build
```

- A API fica disponível por padrão em `http://localhost:8000`.
- RabbitMQ Management: `http://localhost:15672`.

Consulte `docs/instalacao.md` para detalhes sobre variáveis de ambiente e opções avançadas.

---

## 🧪 Execução local (desenvolvimento)
```bash
cd api
python -m venv .venv
. .venv/Scripts/activate   # Windows
pip install -r requirements.txt
python -m spacy download pt_core_news_lg
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- Workers e dispatcher (executar em terminais separados):
```bash
python -m app.services.worker
python -m app.services.dispatcher_worker
```

---

## ✉️ Endpoints úteis
- Criar processamento (assincrono):
```http
POST /processing
Content-Type: application/json
{ "originalText": "Texto a ser analisado", "externalId": "opcional" }
```
- Processar inline (sincrono, para testes):
```http
POST /processing/now
Content-Type: application/json
{ "originalText": "O telefone é 619954324" }
```
- Consultar processamento:
```http
GET /processing/{id}
GET /processing/external/{external_id}
```

---

## ✅ Testes
Executar a suíte de testes:
```bash
cd api
pytest -q
```
Há conjuntos de amostra em `api/tests/challange/files/`.

---

## 📈 Observabilidade e carga
A arquitetura foi testada com k6 (carga leve e alta). Em baixa concorrência a latência end-to-end foi baixa; em alta concorrência a latência aumentou devido ao tempo de processamento assíncrono (veja `docs/arquitetura.md` para detalhes das medições).

---

## ♻️ Contribuição
- Abra issues descrevendo o problema ou melhoria desejada.
- Para PRs: crie uma branch por tema, inclua testes e atualize a documentação.

---

## 🔒 Nota sobre uso e dados
Este projeto foi desenvolvido para fins do Hackathon. Ao testar com dados reais, respeite regulamentações e privacidade — e tome cuidado com chaves e segredos em `.env`.

---

Se quiser, eu adiciono exemplos de payloads com respostas de exemplo, badges de CI e uma seção de troubleshooting. Deseja que eu inclua algo mais? 🎯