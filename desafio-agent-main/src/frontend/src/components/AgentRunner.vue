<script setup lang="ts">
import { onMounted } from "vue"
import { useAgentRunnerStore } from "../stores/agentRunnerStore"
import CostHistory from "./CostHistory.vue"

const store = useAgentRunnerStore()

onMounted(() => {
  store.fetchAgents()
})
</script>

<template>
  <div class="agent-runner">
    <h2>Executar Agente</h2>

    <div class="form-row">
      <label for="agent">Agente:</label>
      <select v-model="store.selectedAgentId" id="agent">
        <option v-for="agent in store.agents" :key="agent.id" :value="agent.id">
          {{ agent.name }} ({{ agent.model }})
        </option>
      </select>
    </div>

    <div class="form-row">
      <label for="question">Pergunta:</label>
      <input v-model="store.question" id="question" placeholder="Digite sua pergunta..." />
    </div>

    <div class="buttons">
      <button @click="store.askAgent" :disabled="!store.selectedAgentId || !store.question || store.loading">
        {{ store.loading ? "Perguntando..." : "Perguntar" }}
      </button>
      <button @click="store.clearMemory" :disabled="!store.selectedAgentId || store.loading" class="btn-clear">
        🧹 Limpar Memória
      </button>
    </div>

    <div v-if="store.loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>

    <div v-if="store.answer" class="response-box">
      <h3>Resposta:</h3>
      <p v-if="store.agentInfo">
        <strong>Agente:</strong> {{ store.agentInfo.name }} ({{ store.agentInfo.provider }})
      </p>
      <pre>{{ store.answer }}</pre>
    </div>

    <div v-if="store.memory.length > 0" class="memory-box">
      <h3>Memória usada:</h3>
      <ul>
        <li v-for="(m, idx) in store.memory" :key="idx">
          <strong>Você:</strong> {{ m.input }} <br />
          <strong>Resposta:</strong> {{ m.output }} <br />
          <small v-if="m.agent_name">[{{ m.agent_name }} / {{ m.provider }}]</small>
        </li>
      </ul>
    </div>

    <CostHistory />
  </div>
</template>

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