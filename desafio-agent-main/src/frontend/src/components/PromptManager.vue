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
          <pre style="white-space: pre-wrap;">{{ testResults[prompt.id] }}</pre>
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

  <CostHistory :summary="costSummary" />

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Aguarde, processando...</span>
    </div>

    <Toast v-if="toast.message" :message="toast.message" :type="toast.type" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import CostHistory from "./CostHistory.vue";
import { useToast } from "vue-toastification"

const toast = useToast()

const apiBase = "http://localhost:8000/api/v1/prompts";
const apiAgents = "http://localhost:8000/api/v1/agents";

const prompts = ref<any[]>([]);
const agents = ref<any[]>([]);
const testResults = ref<{ [key: string]: string }>({});

const answer = ref<string>("");
const memory = ref<any[]>([]);
const costSummary = ref({ total_cost: 0, average_cost: 0, executions: 0 });
const loading = ref(false);
const agentInfo = ref<{ name: string; provider: string } | null>(null);

const newPrompt = ref({
  name: "",
  description: "",
  content: "",
  version: "1.0"
});

const selectedAgentId = ref<string | null>(null);

async function fetchPrompts() {
  try {
    const res = await fetch(apiBase);
    prompts.value = await res.json();
  } catch (err: any) {
    toast.error("Ocorreu o erro: " + err.message)
  }
}

async function fetchAgents() {
  try {
    const res = await fetch(apiAgents);
    agents.value = await res.json();
  } catch (err) {
    toast.error('Ocorreu o erro: ' + err);
  }
}

async function fetchCosts(agentId: string) {
  const res = await fetch(`http://localhost:8000/api/v1/agents/${agentId}/costs/summary`);
  if (!res.ok) return;
  const data = await res.json();
  costSummary.value = data;
}

async function createPrompt() {
  if (!selectedAgentId.value) {
    toast.warning("Selecione um agente antes de criar o prompt.");
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

    toast.success("Prompt criado com sucesso!");
  } catch (err: any) {
    toast.error("Ocorreu o erro: " + err.message)
  }
}

async function testPrompt(promptId: string) {
  loading.value = true
  answer.value = ""
  memory.value = []

  const prompt = prompts.value.find(p => p.id === promptId)
  if (!prompt) {
    toast.error("Prompt não foi encontrado.")
    loading.value = false
    return
  }

  if (!prompt.agent_id) {
    toast.error("Este prompt não está vinculado a um agente.")
    loading.value = false
    return
  }

  try {
    const res = await fetch(`${apiAgents}/${prompt.agent_id}/run/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ input: prompt.content })
    })

    if (!res.ok || !res.body) {
      const errorData = await res.json().catch(() => ({}))
      if (res.status === 402) {
        toast.error("💳 Sem créditos: " + (errorData.detail || "Conta OpenAI sem saldo."))
      } else if (res.status === 401) {
        toast.error("🔑 Erro de autenticação: " + (errorData.detail || "Chave de API inválida."))
      } else {
        toast.error("⚠️ Erro: " + (errorData.detail || "Falha ao executar prompt"))
      }
      loading.value = false
      return
    }

    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""
    let streamedText = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const parts = buffer.split("\n")
      buffer = parts.pop() || ""

      for (const part of parts) {
        if (!part.trim()) continue
        const msg = JSON.parse(part)

        if (msg.type === "error") {
          toast.error(msg.message)
          loading.value = false
          return
        }

        if (msg.type === "token") {
          streamedText += msg.content
          testResults.value[promptId] = streamedText
        }

        if (msg.type === "end") {
          testResults.value[promptId] =
            `Agente: ${msg.agent_name} (${msg.provider})\n\n${msg.answer}`
          memory.value = msg.memory || []
          agentInfo.value = { name: msg.agent_name, provider: msg.provider }
          toast.success("Teste concluído com sucesso!")
          await fetchCosts(prompt.agent_id)
        }
      }
    }
  } catch (err: any) {
    toast.error("❌ Ocorreu o erro: " + err.message)
  } finally {
    loading.value = false
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
button:disabled {
  background: #bbb;
  cursor: not-allowed;
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
.memory-box {
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
.description {
  margin-left: 15px;
}
</style>