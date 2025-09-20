# 🤖 Agent Management Platform (RAG + LangGraph)

**Sistema de Gestão de Agentes de IA com LangGraph e RAG (Retrieval-Augmented Generation)**

## 📋 Descrição do Projeto

API desenvolvida como desafio técnico.  
O sistema permite a criação, gestão e orquestração de agentes de Inteligência Artificial utilizando **LangGraph** e **RAG**, com suporte a:

- ✅ CRUD completo para gerenciamento de prompts e agentes
- ✅ Orquestração de agentes com **LangGraph**
- ✅ Integração RAG para contextualização de respostas
- ✅ **Busca semântica de documentos** via Chroma Vector DB
- ✅ **FastAPI microservice** para consultas com contexto
- ✅ Integração com bases de conhecimento externas
- ✅ **Streaming de respostas** e **histórico de interações**
- ✅ **Cálculo de custos** por transação e total geral

---

## 🚀 Tecnologias Utilizadas

- **Node.js** (API principal)
- **Vue.js** (Frontend)
- **PostgreSQL** (Banco de dados relacional)
- **LangGraph** (Orquestrador de agentes)
- **FastAPI** (Microserviço RAG)
- **ChromaDB** (Vector Database)
- **Docker Compose** (Orquestração de containers)

---

## 🐳 Como Rodar o Projeto com Docker

### 1. Clonar o repositório
```bash
git clone https://github.com/RonaldoAmaralDev/desafio-agent.git
cd desafio-agent
```

### 2. Configurar variáveis de ambiente
Copie o arquivo `.env.example` para `.env` e ajuste os valores conforme necessário:

```bash
cp .env.example .env
```

### 3. Subir os containers
```bash
docker compose up --build
```

Isso vai iniciar:
- **API Node.js** → porta `3000`
- **Banco Postgres** → porta `5432`
- **Chroma Vector DB** → porta `8000`
- **FastAPI RAG microservice** → porta `8001`

### 4. Acessar a aplicação
- Frontend: `http://localhost:5173`
- Postgres: `porta 5432`
- API Principal: `http://localhost:8000/api`
- ChromaDB: `http://localhost:8005`

---

## 📖 Exemplos de Uso

### 1. CRUD de Prompts
Crie, atualize, liste e remova prompts diretamente pela API Node.js.

### 2. Consulta via RAG
Envie uma pergunta ao **microserviço FastAPI** que consulta documentos no **ChromaDB** e retorna respostas contextualizadas com suporte da LLM.

Exemplo de requisição:
```bash
curl --location 'http://localhost:8001/api/assistant/query' --header 'Content-Type: application/json' --data '{"question": "Quem foi Pedro Álvares Cabral?"}'
```

Resposta (exemplo):
```json
{
  "answer": "Pedro Álvares Cabral foi um navegador e explorador português que viveu no século XV. Ele é famoso por ter descoberto o Brasil..."
}
```

---

## 📌 Decisões de Arquitetura

- Separação de responsabilidades entre **API principal** (gestão CRUD) e **microserviço RAG** (consultas inteligentes)
- Persistência de contexto e documentos em **ChromaDB**
- Uso de **LangGraph** para orquestrar agentes e fluxos de execução
- Integração transparente via **Docker Compose**
- **Streaming de respostas** para queries longas
- **Cálculo de custos por request e acumulado** (controle de uso de tokens e billing)

---

## 🧪 Testes

Para rodar os testes unitários e de integração:

1. Acesse o container da API:
```bash
docker exec -it desafio-agent-api bash
```

2. Execute os testes com cobertura:
```bash
pytest tests/ --cov=src
```

---

## 🔄 Reset do Banco de Dados

Caso tenha interesse em limpar o banco de dados:
```bash
chmod +x scripts/reset-db.sh
./scripts/reset-db.sh
```

---

## 👨‍💻 Autor

Desenvolvido por **Ronaldo Amaral**  
🔗 [LinkedIn](https://www.linkedin.com/in/ronaldo-amaral/)  
🔗 [GitHub](https://github.com/RonaldoAmaralDev)