<template>
  <div class="prompt-manager">
    <h2>Gestão de Prompts</h2>

    <div class="form-card">
      <h3>Criar novo prompt</h3>
      <form @submit.prevent="createPrompt" class="form-grid">
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

        <div class="form-group">
          <label for="prompt-description">Descrição</label>
          <input id="prompt-description" v-model="newPrompt.description" placeholder="Descrição" />
        </div>

        <div class="form-group">
          <label for="prompt-content">Conteúdo do prompt</label>
          <textarea id="prompt-content" v-model="newPrompt.content" placeholder="Conteúdo do prompt" required></textarea>
        </div>

        <button type="submit" class="btn-create">Criar Prompt</button>
      </form>
    </div>

    <div class="prompts-list">
      <h3>Prompts existentes</h3>
      <div v-for="prompt in prompts" :key="prompt.id" class="prompt-card">
        <div class="prompt-header">
          <strong>{{ prompt.name }}</strong>
          <span class="description">{{ prompt.description }}</span>
        </div>
        <div class="prompt-actions">
          <button @click="testPrompt(prompt.id)" class="btn-test" :disabled="loading">
            {{ loading ? "Testando..." : "Testar" }}
          </button>
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
          <strong>Resposta:</strong> {{ m.output }} <br />
          <small v-if="m.agent_name">[{{ m.agent_name }} / {{ m.provider }}]</small>
        </li>
      </ul>
    </div>

    <CostHistory />

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { storeToRefs } from "pinia";
import { useToast } from "vue-toastification";

import { usePromptStore } from "../stores/promptStore";
import { useAgentRunnerStore } from "../stores/agentRunnerStore";
import CostHistory from "./CostHistory.vue";

const toast = useToast();

// Stores
const promptStore = usePromptStore();
const agentStore = useAgentRunnerStore();

const { prompts, loading } = storeToRefs(promptStore);
const { agents, memory, agentInfo, answer } = storeToRefs(agentStore);

const newPrompt = ref({ name: "", description: "", content: "", version: "1.0" });
const selectedAgentId = ref<string | null>(null);
const testResults = ref<{ [key: string]: string }>({});

async function createPrompt() {
  if (!selectedAgentId.value) {
    toast.warning("Selecione um agente antes de criar o prompt.");
    return;
  }

  try {
    await promptStore.createPrompt({ ...newPrompt.value, agent_id: selectedAgentId.value });
    newPrompt.value = { name: "", description: "", content: "", version: "1.0" };
    selectedAgentId.value = null;
  } catch {
  }
}

async function testPrompt(promptId: string) {
  loading.value = true;
  try {
    const prompt = prompts.value.find((p) => p.id === promptId);
    if (!prompt) throw new Error("Prompt não encontrado");
    if (!prompt.agent_id) throw new Error("Este prompt não está vinculado a um agente");

    agentStore.question = prompt.content;
    agentStore.selectedAgentId = prompt.agent_id;
    await agentStore.askAgent();

    testResults.value[promptId] =
      `Agente: ${agentInfo.value?.name} (${agentInfo.value?.provider})\n\n${answer.value}`;
    toast.success("Teste concluído com sucesso!");
  } catch (err: any) {
    toast.error("❌ Erro ao testar prompt: " + err.message);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  promptStore.fetchPrompts();
  agentStore.fetchAgents();
});
</script>

<style scoped>
.prompt-manager {
  font-family: Arial, sans-serif;
  padding: 20px;
  max-width: 800px;
  margin: auto;
}
h2, h3 { color: #333; }
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
.form-grid { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: flex; gap: 12px; }
.form-group { display: flex; flex-direction: column; flex: 1; }
input, select, textarea {
  padding: 10px 12px; border: 1px solid #ccc; border-radius: 6px;
  font-size: 1em; width: 100%; box-sizing: border-box;
}
select { height: 42px; }
textarea { min-height: 100px; resize: vertical; }
button {
  padding: 10px 16px; border: none; border-radius: 6px;
  cursor: pointer; font-weight: 500;
}
.btn-create { background-color: #4caf50; color: white; }
.btn-create:hover { background-color: #45a049; }
.btn-test { background-color: #2196f3; color: white; }
.btn-test:hover { background-color: #1976d2; }
button:disabled { background: #bbb; cursor: not-allowed; }
.test-result {
  margin-top: 10px; padding: 10px;
  background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 6px;
}
.test-result pre {
  white-space: pre-wrap; word-wrap: break-word;
  font-family: inherit; margin: 0;
}
.memory-box {
  margin-top: 1.5rem; padding: 1rem;
  background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 6px;
}
.memory-box ul { list-style: none; padding: 0; }
.memory-box li {
  margin-bottom: 10px; background: #fff;
  padding: 8px; border-radius: 6px; border: 1px solid #ddd;
}
.description { margin-left: 15px; }
.loading {
  margin-top: 1rem; display: flex; align-items: center; gap: 10px;
  color: #555; font-style: italic;
}
.spinner {
  width: 20px; height: 20px;
  border: 3px solid #ccc; border-top: 3px solid #2196f3;
  border-radius: 50%; animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>
