<script setup lang="ts">
import { ref } from "vue"
import { useAgentStore } from "../stores/agentStore"

const agentStore = useAgentStore()
const importFile = ref<File | null>(null)

function handleImport() {
  if (importFile.value) {
    agentStore.importAgents(importFile.value)
  }
}
</script>

<template>
  <div class="export-import-card">
    <h2>Exportar / Importar Agentes</h2>

    <div class="actions">
      <button :disabled="agentStore.downloading" @click="agentStore.exportAgents">
        <span v-if="agentStore.downloading">⏳ Baixando...</span>
        <span v-else>⬇️ Exportar (JSON)</span>
      </button>
    </div>

    <div class="actions">
      <input
        type="file"
        accept="application/json"
        @change="(e:any) => importFile.value = e.target.files?.[0] || null"
      />
      <button :disabled="agentStore.importing || !importFile" @click="handleImport">
        <span v-if="agentStore.importing">⏳ Importando...</span>
        <span v-else>⬆️ Importar JSON</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.export-import-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  background: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}
.actions {
  margin-top: 16px;
  display: flex;
  gap: 10px;
  align-items: center;
}
button {
  padding: 10px 16px;
  background: #1e88e5;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}
button:hover:not(:disabled) {
  background: #1565c0;
}
</style>
