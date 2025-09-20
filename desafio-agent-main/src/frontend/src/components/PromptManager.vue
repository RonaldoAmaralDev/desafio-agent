<template>
  <div class="prompt-manager">
    <h2>Gestão de Prompts</h2>

    <!-- Formulário de criação -->
    <div class="form-card">
      <h3>Criar novo prompt</h3>
      <form @submit.prevent="createPrompt" class="form-grid">

        <!-- Linha com Nome + Agente -->
        <div class="form-row">
          <div class="form-group">
            <label for="prompt-name">Nome</label>
            <input id="prompt-name" v-model="newPrompt.name" placeholder="Nome" required />
          </div>

        <div class="form-group">
        <label for="agent-select">Agente</label>
        <select id="agent-select" v-model="selectedAgentId" v-if="agents.length > 0">
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
            {{ agent.name }}
            </option>
        </select>
        <div v-else class="no-agents">
            Nenhum agente disponível
        </div>
        </div>
        </div>

        <!-- Descrição -->
        <div class="form-group">
          <label for="prompt-description">Descrição</label>
          <input id="prompt-description" v-model="newPrompt.description" placeholder="Descrição" />
        </div>

        <!-- Conteúdo -->
        <div class="form-group">
          <label for="prompt-content">Conteúdo do prompt</label>
          <textarea id="prompt-content" v-model="newPrompt.content" placeholder="Conteúdo do prompt" required></textarea>
        </div>

        <button type="submit" class="btn-create">Criar Prompt</button>
      </form>
    </div>

    <!-- Lista de prompts -->
    <div class="prompts-list">
      <h3>Prompts existentes</h3>
      <div v-for="prompt in prompts" :key="prompt.id" class="prompt-card">
        <div class="prompt-header">
          <strong>{{ prompt.name }}</strong>
          <span class="description">{{ prompt.description }}</span>
        </div>
        <div class="prompt-actions">
          <button @click="testPrompt(prompt.id)" class="btn-test">Testar</button>
        </div>
        <div v-if="testResults[prompt.id]" class="test-result">
          <strong>Resultado:</strong> {{ testResults[prompt.id] }}
        </div>
      </div>
    </div>

    <Toast v-if="toast.message" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Toast from "./Toast.vue";

const apiBase = "http://localhost:8000/api/v1/prompts";
const apiAgents = "http://localhost:8000/api/v1/agents"; // endpoint para agentes

const prompts = ref([]);
const agents = ref([]);
const testResults = ref({});
const toast = ref({ message: "", type: "info" });

const newPrompt = ref({
  name: "",
  description: "",
  content: "",
  version: "1.0"
});

const selectedAgentId = ref(null);

// Buscar prompts existentes
async function fetchPrompts() {
  try {
    const res = await fetch(apiBase);
    prompts.value = await res.json();
  } catch (err) {
    toast.value = { message: "Erro ao buscar prompts.", type: "error" };
  }
}

// Buscar agentes
async function fetchAgents() {
  try {
    const res = await fetch(apiAgents);
    agents.value = await res.json();
  } catch (err) {
    toast.value = { message: "Erro ao buscar agentes.", type: "error" };
  }
}

// Criar novo prompt
async function createPrompt() {
  if (!selectedAgentId.value) {
    toast.value = { message: "Selecione um agente antes de criar o prompt", type: "warning" };
    return;
  }

  try {
    const res = await fetch(apiBase, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...newPrompt.value, agent_id: selectedAgentId.value })
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "Erro ao criar prompt");
    }

    const data = await res.json();
    prompts.value.push(data);
    newPrompt.value = { name: "", description: "", content: "", version: "1.0" };
    selectedAgentId.value = null;

    toast.value = { message: "Prompt criado com sucesso!", type: "success" };
  } catch (err) {
    toast.value = { message: err.message, type: "error" };
  }
}

// Testar prompt
async function testPrompt(promptId) {
  if (!selectedAgentId.value) return;

  try {
    const res = await fetch(`${apiBase}/test/${selectedAgentId.value}/${promptId}`, { method: "POST" });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Erro ao testar prompt");
    }

    const data = await res.json();
    testResults.value[promptId] = data.output;

    toast.value = { message: "Teste realizado com sucesso!", type: "success" };
  } catch (err) {
    toast.value = { message: err.message, type: "error" };
  }
}

// Executa ao montar o componente
onMounted(() => {
  fetchPrompts();
  fetchAgents();
});
</script>


<style scoped>
.prompt-manager {
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 800px;
  margin: auto;
}

h2, h3 {
  color: #333;
}

/* Cards */
.form-card, .prompt-card {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.no-agents {
  padding: 10px;
  color: #999;
  font-style: italic;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: #f3f3f3;
}

/* Grid do formulário */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.form-group {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.form-group label {
  font-weight: 500;
  margin-bottom: 4px;
}

input, select, textarea {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1em;
  width: 100%;
  box-sizing: border-box;
}

select {
  height: 42px;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

/* Botões */
button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.btn-create {
  background-color: #4caf50;
  color: white;
}

.btn-create:hover {
  background-color: #45a049;
}

.btn-test {
  background-color: #2196f3;
  color: white;
}

.btn-test:hover {
  background-color: #1976d2;
}

/* Lista de prompts */
.prompts-list .prompt-card {
  display: flex;
  flex-direction: column;
}

.prompt-header {
  font-size: 1.1em;
  margin-bottom: 6px;
}

.description {
  color: #666;
  font-size: 0.9em;
  margin-left: 5px;
}

.test-result {
  margin-top: 10px;
  padding: 10px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 6px;
}
</style>
