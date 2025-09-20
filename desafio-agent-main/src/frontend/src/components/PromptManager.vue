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
          <button @click="testPrompt(prompt.id)" class="btn-test" :disabled="loading">Testar</button>
        </div>
        <div v-if="testResults[prompt.id]" class="test-result">
          <strong>Resultado:</strong>
          <pre>{{ testResults[prompt.id] }}</pre>
        </div>
      </div>
    </div>

    <div v-if="memory.length > 0" class="memory-box">
      <h3>Memória usada:</h3>
      <ul>
        <li v-for="(m, idx) in memory" :key="idx">
          <strong>Você:</strong> {{ m.input }} <br />
          <strong>Agente:</strong> {{ m.output }}
        </li>
      </ul>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>

    <Toast v-if="toast.message" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Toast from "./Toast.vue";

const apiBase = "http://localhost:8000/api/v1/prompts";
const apiAgents = "http://localhost:8000/api/v1/agents";

const prompts = ref([]);
const agents = ref([]);
const testResults = ref({});
const toast = ref({ message: "", type: "info" });

const answer = ref<string>("");
const memory = ref<any[]>([]);
const loading = ref(false);

const newPrompt = ref({
  name: "",
  description: "",
  content: "",
  version: "1.0"
});

const selectedAgentId = ref(null);

async function fetchPrompts() {
  try {
    const res = await fetch(apiBase);
    prompts.value = await res.json();
  } catch (err) {
    toast.value = { message: "Erro ao buscar prompts.", type: "error" };
  }
}

async function fetchAgents() {
  try {
    const res = await fetch(apiAgents);
    agents.value = await res.json();
  } catch (err) {
    toast.value = { message: "Erro ao buscar agentes.", type: "error" };
  }
}

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

async function testPrompt(promptId) {
  loading.value = true;
  answer.value = "";
  memory.value = [];

  const prompt = prompts.value.find(p => p.id === promptId);
  if (!prompt) {
    toast.value = { message: "Prompt não encontrado.", type: "error" };
    return;
  }

  if (!prompt.agent_id) {
    toast.value = { message: "Este prompt não está vinculado a um agente.", type: "warning" };
    return;
  }

  try {
    const res = await fetch(`${apiAgents}/${prompt.agent_id}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: prompt.content })
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Erro ao executar prompt");
    }

    const data = await res.json();
    testResults.value[promptId] = data.answer;
    memory.value = data.memory || [];

    toast.value = { message: "Teste realizado com sucesso!", type: "success" };
  } catch (err) {
    toast.value = { message: err.message, type: "error" };
  } finally {
    loading.value = false;
  }
}

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

.test-result pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
}

button:disabled {
  background: #bbb;
  cursor: not-allowed;
}
.loading {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #555;
  font-style: italic;
}
.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid #ccc;
  border-top: 3px solid #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.response-box, .memory-box {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 6px;
}
.memory-box ul {
  list-style: none;
  padding: 0;
}
.memory-box li {
  margin-bottom: 10px;
  background: #fff;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ddd;
}
</style>
