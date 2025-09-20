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

    <div class="buttons">
      <button @click="askAgent" :disabled="!selectedAgentId || !question || loading">
        {{ loading ? "Perguntando..." : "Perguntar" }}
      </button>
      <button @click="clearMemory" :disabled="!selectedAgentId || loading" class="btn-clear">
        🧹 Limpar Memória
      </button>
    </div>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>

    <div v-if="answer" class="response-box">
      <h3>Resposta:</h3>
      <pre>{{ answer }}</pre>
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

    <CostHistory :summary="costSummary" />

    <Toast v-if="toast.message" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useToast } from "vue-toastification"
import CostHistory from "./CostHistory.vue";

const toast = useToast()

const apiAgents = "http://localhost:8000/api/v1/agents";

const agents = ref<any[]>([]);
const selectedAgentId = ref<string>("");
const question = ref<string>("");
const answer = ref<string>("");
const memory = ref<any[]>([]);
const loading = ref(false);

const costSummary = ref({ total_cost: 0, average_cost: 0, executions: 0 });

async function fetchAgents() {
  try {
    const res = await fetch(apiAgents);
    agents.value = await res.json();
    if (agents.value.length > 0) {
      selectedAgentId.value = agents.value[0].id;
    }
  } catch (err: any) {
    toast.error("Ocorreu o erro: " + err.message)
  }
}

async function fetchCosts(agentId: string) {
  const res = await fetch(`http://localhost:8000/api/v1/agents/${agentId}/costs/summary`);
  if (!res.ok) return;
  const data = await res.json();
  costSummary.value = data;
}

async function askAgent() {
  loading.value = true;
  answer.value = "";
  memory.value = [];

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
    memory.value = data.memory || [];

    toast.success("Execução realizada com sucesso!");

    await fetchCosts(selectedAgentId.value);
  } catch (err: any) {
    toast.error("Ocorreu o erro: " + err.message)
  } finally {
    loading.value = false;
  }
}

async function clearMemory() {
  if (!selectedAgentId.value) return;

  loading.value = true;
  try {
    const res = await fetch(`${apiAgents}/${selectedAgentId.value}/memory`, {
      method: "DELETE"
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || "Erro ao limpar memória");
    }

    await res.json();
    memory.value = [];
    toast.success("Memória limpa com sucesso!");
  } catch (err: any) {
    toast.error("Ocorreu o erro: " + err.message)
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchAgents();
});
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
.buttons {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
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
.btn-clear {
  background-color: #f44336;
  color: white;
}
.btn-clear:hover {
  background-color: #d32f2f;
}
.response-box pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  margin: 0;
}
</style>