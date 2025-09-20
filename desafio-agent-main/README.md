# 🤖 Agent Management Platform

**Sistema de Gestão de Agentes de IA com LangGraph**

## 📋 Descrição do Projeto

API desenvolvida como desafio técnico para a vaga de Engenheiro(a) de Software Full Stack Sênior. O sistema permite a criação, gestão e orquestração de agentes de Inteligência Artificial utilizando LangGraph, com um CRUD completo para gerenciamento de prompts e configurações dos agentes.

### 🎯 Objetivo

Demonstrar competências em:
- Desenvolvimento backend com Python (FastAPI)
- Implementação de sistemas com IA/LLMs usando LangGraph
- Arquitetura escalável e boas práticas de desenvolvimento
- Gestão de agentes autônomos com diferentes especialidades

## 🏗️ Arquitetura do Sistema

Sistema backend em Python/FastAPI que gerencia:
- **API REST** para operações CRUD de agentes e prompts
- **Sistema de Agentes** com diferentes especializações usando LangGraph
- **Persistência** com PostgreSQL e cache Redis
- **Integração** com modelos de linguagem (OpenAI)
- **Logging** em todas as rotas
- **Middleware** para tratamento de erros e monitoramento
- **CI/CD** para deploy automatizado
- **FrontEnd** para CRUD dos prompts.

## 🚀 Funcionalidades Principais

### 1. Sistema de Agentes com LangGraph

- **Agentes Especializados**: Research, Code e Analysis agents para diferentes tarefas
- **Orquestração**: Coordenação de múltiplos agentes trabalhando em conjunto
- **Workflows com Grafos**: Fluxos complexos com decisões condicionais, loops e execução paralela

### 2. CRUD de Prompts

- **Gestão Completa**: Create, Read, Update, Delete de prompts
- **Versionamento**: Sistema de versões para prompts
- **Validação**: Validação de estrutura e sintaxe dos prompts

### 3. Features

- **RAG (Retrieval-Augmented Generation)**:
  - Integração com bases de conhecimento
  - Busca semântica de documentos
  - Contextualização de respostas

- **Memory Management**:
  - Memória de curto prazo para agentes

## 💻 Stack Tecnológica

- **Python 3.10+**
- **FastAPI**: Framework web assíncrono
- **LangGraph**: Orquestração de agentes
- **SQLAlchemy**: ORM
- **PostgreSQL**: Banco de dados
- **Redis**: Cache e filas
- **Docker**: Containerização
- **CI/CD**: GitHub Actions para integração e deploy automáticos
- **Vue 3 + Vite**: Framework Front-End para o CRUD dos prompts.
- **Nginx**: Para apoio no Front-end.

## 🔧 Configuração e Instalação

### Pré-requisitos
- Python 3.10+
- Docker e Docker Compose
- PostgreSQL 15+
- Redis 7+

### Setup Local

1. **Clone o repositório**
```bash
git clone https://github.com/RonaldoAmaralDev/desafio-agent.git
cd desafio-agent
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. **Inicie com Docker Compose**
```bash
docker compose up --build
```

4. **Acesse a API**
- API Docs: http://localhost:8005/docs
- Health Check: http://localhost:8005/health

5. **Acesse a interface de Prompt Engineering**
- Frontend: http://localhost:5173

## 📊 Exemplos de Uso

### Criando um Agente
```python
POST /api/v1/agents
{
  "name": "Research Assistant",
  "model": "gpt-4o",
  "temperature": 0.7,
  "prompt_id": "uuid-do-prompt"
}
```

### Executando um Workflow
```python
POST /api/v1/executions
{
  "agent_id": "agent-1",
  "input": "Analise as tendências de mercado em IA"
}
```

## 🧪 Testes

```bash
pytest tests/ --cov=src
```

## 📈 Diferenciais Implementados

1. **Multi-Agent Collaboration**: Agentes podem colaborar entre si para resolver tarefas complexas
2. **Prompt Engineering Interface**: Interface visual para criação e teste de prompts
3. **Real-time Monitoring**: Acompanhamento em tempo real das execuções
4. **Cost Tracking**: Monitoramento de custos por execução/agente
5. **Export/Import**: Sistema de export/import de configurações de agentes
6. **Logging em todas as rotas**: Monitoramento detalhado das requisições
7. **Middleware**: Tratamento centralizado de erros e métricas
8. **CI/CD**: Integração e deploy automatizados



## 📝 Notas sobre o Desafio

Este projeto foi desenvolvido como resposta ao desafio técnico, demonstrando:

1. **Competência Backend**: API robusta e bem estruturada com FastAPI
2. **Conhecimento em IA**: Uso prático de LangGraph e técnicas de RAG
3. **Arquitetura Escalável**: Design pensado para crescimento e manutenibilidade
4. **Boas Práticas**: Clean code, testes, documentação e containerização
5. **Visão de Produto**: Features que agregam valor real ao usuário final