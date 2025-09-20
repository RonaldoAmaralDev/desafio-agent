# 🤖 Agent Management Platform

**Sistema de Gestão de Agentes de IA com LangGraph + RAG**

## 📋 Descrição do Projeto

API desenvolvida como desafio técnico.  
O sistema permite a **criação, gestão e orquestração de agentes de Inteligência Artificial** utilizando **LangGraph**, com CRUD completo de prompts, integração com **RAG** (Retrieval-Augmented Generation), **memória de curto prazo** e **monitoramento de custos**.  

### 🎯 Objetivo  

Demonstrar competências em:  
- Desenvolvimento backend com **Python (FastAPI)**  
- Implementação de sistemas com **IA/LLMs (LangGraph + RAG)**  
- Arquitetura escalável e boas práticas de desenvolvimento  
- Gestão de agentes autônomos com especialidades diferentes  
- Integração **frontend/backend** (Vue 3 + Vite)  
- Observabilidade (logging, monitoramento de custos)  

---

## 🏗️ Arquitetura do Sistema  

- **API REST (FastAPI)** → CRUD de agentes e prompts  
- **LangGraph** → Orquestração de agentes autônomos  
- **RAG** → Busca semântica e contextualização via ChromaDB  
- **Persistência** → PostgreSQL (dados) + Redis (memória/cache)  
- **LLM Provider** → Ollama (modelos locais: *Llama3*, *nomic-embed-text*) e OpenAI GPT
- **Frontend** → Vue 3 + Vite (CRUD de prompts e execução de agentes)  
- **Infra** → Docker + Docker Compose + GitHub Actions (CI/CD)  

---

## 🚀 Funcionalidades Principais  

### 1. **Agentes Autônomos (LangGraph)**  
- Agentes especializados em diferentes tarefas  
- Execução via `/api/v1/agents/{id}/run`  
- Configuração dinâmica: modelo, temperatura, base_url  
- **Multi-Agent Collaboration**: agentes podem cooperar para resolver tarefas complexas  

### 2. **CRUD de Prompts**  
- Criar, editar, listar e excluir prompts  
- Versionamento básico  
- Teste de prompts direto pela interface  

### 3. **RAG (Retrieval-Augmented Generation)**  
- Upload de documentos (PDF, TXT, MD) via `/api/v1/rag/upload`  
- Consulta contextualizada via `/api/v1/rag/query`  
- Indexação persistente em `chroma_db/`  

### 4. **Memory Management**  
- Histórico de conversas salvo no **Redis**  
- Suporte a memória de curto prazo por agente  
- Endpoint para limpar memória: `DELETE /api/v1/agents/{id}/memory`  

### 5. **Cost Tracking**  
- Registro de custos simulados por execução  
- API de custos:  
  - `/api/v1/agents/{id}/costs` → histórico detalhado  
  - `/api/v1/agents/{id}/costs/summary` → resumo total, média e nº de execuções  
- Visualização dos custos direto no frontend  

### 6. **Export/Import de Agentes** *(planejado)*  
- Exportar configuração de agentes (JSON)  
- Importar para replicar ambientes  

---

## 💻 Stack Tecnológica  

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, LangGraph, LangChain  
- **Banco**: PostgreSQL 15  
- **Cache/Memória**: Redis 7  
- **Vector DB**: ChromaDB  
- **LLM**: Ollama (modelos locais) e OpenAI GPT
- **Frontend**: Vue 3 + Vite  
- **Infra**: Docker, Docker Compose, GitHub Actions  

---

## 🔧 Configuração e Instalação  

### Pré-requisitos  
- Docker e Docker Compose  
- Python 3.10+ (opcional para rodar local)  
- PostgreSQL 15+  
- Redis 7+  

### Setup Local  
```bash
git clone https://github.com/RonaldoAmaralDev/desafio-agent.git
cd desafio-agent
cp .env.example .env
# edite variáveis do .env se necessário
docker compose up --build
```

### Acesso  
- API: [http://localhost:8000/docs](http://localhost:8000/docs)  
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)  
- Frontend: [http://localhost:5173](http://localhost:5173)  

---

## 📊 Exemplos de Uso  

### Criar Agente  
```http
POST /api/v1/agents
{
  "name": "Research Assistant",
  "model": "llama3",
  "temperature": 0.7
}
```

### Executar Agente  
```http
POST /api/v1/agents/{agent_id}/run
{
  "input": "Explique a importância da Revolução Industrial"
}
```

### Consultar Custos  
```http
GET /api/v1/agents/{agent_id}/costs/summary
```

### Upload de Documento  
```http
POST /api/v1/rag/upload
(file=@documento.pdf)
```

---

## 🧪 Testes  
```bash
pytest tests/ --cov=src
```

---

## 📈 Diferenciais Implementados  
- Multi-Agent Collaboration  
- Prompt Engineering Interface (frontend Vue)  
- RAG integrado (Chroma + Ollama | OpenAI GPT)  
- Memory Management com Redis  
- Cost Tracking por execução/agente  
- Logging em todas as rotas  
- Middleware de erros customizado  
- CI/CD configurado (GitHub Actions)  
- Persistência para embeddings (Chroma) e modelos (Ollama, OpenAI GPT)  

---

## 🗺️ Roadmap Futuro  
1. **Memory Management Completo**: manter histórico por sessão/usuário  
2. **Export/Import de Agentes**  
3. **Dashboard em tempo real**: execuções e custos  
4. **Suporte a múltiplos providers**: OpenAI, Azure, Anthropic  
5. **Frontend Avançado**: upload de docs e workflows visuais  

---

## 📝 Notas sobre o Desafio  
Este projeto foi desenvolvido como resposta ao desafio técnico, demonstrando:  
- **Competência Backend** com FastAPI e SQLAlchemy  
- **Conhecimento em IA** com LangGraph + RAG  
- **Boas Práticas**: testes, logging, documentação, Docker  
- **Visão de Produto**: backend + frontend + LLMs integrados em um sistema único