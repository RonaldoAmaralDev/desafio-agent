<template>
  <div class="agent-runner">
    <h2>Executar Agente</h2>

    <div class="form-row">
      <label for="agent">Agente:</label>
      <select v-model="selectedAgentId" id="agent">
        <option v-for="agent in agents" :key="agent.id" :value="agent.id">
          {{ agent.name }} ({{ agent.model }})
        </option>
      </select>
    </div>

    <div class="form-row">
      <label for="question">Pergunta:</label>
      <input v-model="question" id="question" placeholder="Digite sua pergunta..." />
    </div>

    <button @click="askAgent" :disabled="!selectedAgentId || !question || loading">
      Perguntar
    </button>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>

    <!-- Resposta -->
    <div v-if="answer" class="response-box">
      <h3>Resposta:</h3>
      <pre>{{ answer }}</pre>
    </div>

    <Toast v-if="toast.message" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import Toast from "./Toast.vue";

const apiAgents = "http://localhost:8000/api/v1/agents";

const agents = ref<any[]>([]);
const selectedAgentId = ref<string>("");
const question = ref<string>("");
const answer = ref<string>("");
const toast = ref({ message: "", type: "info" });
const loading = ref(false);

async function fetchAgents() {
  try {
    const res = await fetch(apiAgents);
    agents.value = await res.json();
    if (agents.value.length > 0) {
      selectedAgentId.value = agents.value[0].id;
    }
  } catch (err) {
    toast.value = { message: "Erro ao buscar agentes.", type: "error" };
  }
}

async function askAgent() {
  loading.value = true;
  answer.value = "";

  try {
    const res = await fetch(`${apiAgents}/${selectedAgentId.value}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: question.value })
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Erro ao executar agente");
    }

    const data = await res.json();
    answer.value = data.answer;

    toast.value = { message: "Execução realizada com sucesso!", type: "success" };
  } catch (err: any) {
    toast.value = { message: err.message, type: "error" };
  } finally {
    loading.value = false;
  }
}

onMounted(fetchAgents);
</script>

<style scoped>
.agent-runner {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  background: #fafafa;
}
.form-row {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}
label {
  font-weight: 500;
  margin-bottom: 4px;
}
input, select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
}
button {
  padding: 10px 16px;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
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
.response-box {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 6px;
}
.response-box pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
}
</style>
