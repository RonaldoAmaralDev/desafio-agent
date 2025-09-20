# 🤖 Agent Management Platform

**Sistema de Gestão de Agentes de IA com LangGraph + RAG**

## 📋 Descrição do Projeto

API desenvolvida como desafio técnico para a vaga de Engenheiro(a) de Software Full Stack Sênior.  
O sistema permite a criação, gestão e orquestração de agentes de Inteligência Artificial utilizando **LangGraph**, com um CRUD completo para gerenciamento de prompts, integração com **RAG** (Retrieval-Augmented Generation) e interface visual para manipulação de prompts.

### 🎯 Objetivo

Demonstrar competências em:
- Desenvolvimento backend com Python (FastAPI)
- Implementação de sistemas com IA/LLMs (LangGraph + RAG)
- Arquitetura escalável e boas práticas de desenvolvimento
- Gestão de agentes autônomos com diferentes especialidades
- Integração frontend/backend com Vue 3 + Vite

---

## 🏗️ Arquitetura do Sistema

- **API REST (FastAPI)** → operações CRUD de agentes e prompts  
- **Agentes Autônomos** → orquestrados via LangGraph  
- **RAG** → indexação/consulta de documentos no ChromaDB  
- **Persistência** → PostgreSQL (dados) + Redis (cache/memória)  
- **LLM Provider** → Ollama (Llama3 + embeddings nomic-embed-text)  
- **Frontend** → Vue 3 + Vite para CRUD de prompts e execução de agentes  
- **Infra** → Docker + Docker Compose  
- **Extras** → Logging centralizado, middleware de erros, CI/CD no GitHub Actions  

---

## 🚀 Funcionalidades Principais

### 1. Sistema de Agentes
- Agentes especializados para diferentes tarefas
- Execução via `/api/v1/agents/{id}/run`
- Configuração dinâmica (modelo, temperatura, base_url)

### 2. CRUD de Prompts
- Criar, editar, listar e excluir prompts
- Validação de estrutura
- Versionamento básico

### 3. RAG (Retrieval-Augmented Generation)
- Upload de documentos (PDF, TXT, MD) via `/api/v1/rag/upload`
- Consulta contextualizada via `/api/v1/rag/query`
- Indexação persistente em `chroma_db/`

### 4. Memory Management *(em progresso)*
- Suporte a histórico de conversas (armazenado em Redis)

### 5. Monitoramento e Custos *(planejado)*
- Acompanhamento de execuções
- Cálculo simulado de custo por agente

---

## 💻 Stack Tecnológica

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, LangGraph, LangChain  
- **Banco**: PostgreSQL 15  
- **Cache**: Redis 7  
- **Vector DB**: ChromaDB  
- **LLM**: Ollama (modelos locais)  
- **Frontend**: Vue 3 + Vite  
- **Infra**: Docker, Docker Compose, GitHub Actions (CI/CD)  

---

## 🔧 Configuração e Instalação

### Pré-requisitos
- Docker e Docker Compose
- Python 3.10+ (para rodar local se quiser)
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
- API: http://localhost:8000/docs  
- Health Check: http://localhost:8000/health  
- Frontend: http://localhost:5173  

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

### Upload de Documento
```http
POST /api/v1/rag/upload
(file=@documento.pdf)
```

### Perguntar com RAG
```http
POST /api/v1/rag/query
{
  "question": "O que este documento fala sobre IA?"
}
```

---

## 🧪 Testes
```bash
pytest tests/ --cov=src
```

---

## 📈 Diferenciais Implementados
- Multi-Agent Collaboration (em evolução)
- Prompt Engineering Interface (frontend Vue)
- RAG integrado (Chroma + Ollama)
- Logging em todas as rotas
- Middleware para tratamento de erros
- CI/CD configurado (GitHub Actions)
- Volume persistente para embeddings (Chroma) e modelos (Ollama)

---

## 🗺️ Roadmap Futuro

1. **Memory Management Completo**: manter histórico de conversas em Redis por sessão/usuário.  
2. **Real-time Monitoring**: dashboard de execuções em tempo real.  
3. **Cost Tracking real**: cálculo de custo baseado em tokens gerados.  
4. **Interface Frontend Avançada**: incluir visualização de execuções e upload de documentos direto na interface.  
5. **Suporte a múltiplos providers**: além de Ollama, permitir OpenAI/Azure.  

---

## 📝 Notas sobre o Desafio
Este projeto foi desenvolvido como resposta ao desafio técnico, demonstrando:
- **Competência Backend** com FastAPI e SQLAlchemy  
- **Conhecimento em IA** com LangGraph + RAG  
- **Boas Práticas**: testes, logging, documentação, Docker  
- **Visão de Produto**: integra backend, frontend e LLMs em um sistema único  
