<script setup lang="ts">
import { ref } from "vue"
import { useToast } from "vue-toastification"

const toast = useToast()

const downloading = ref(false)
const importing = ref(false)
const importFile = ref<File | null>(null)

const API = "http://localhost:8000/api/v1";

async function downloadAgents() {
  try {
    downloading.value = true
    const res = await fetch(`${API}/agents/export`)
    if (!res.ok) throw new Error("Falha no export")
    const data = await res.json()

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "agents_export.json"
    a.click()
    URL.revokeObjectURL(url)
    toast.success("Exportação concluída! JSON baixado.")
  } catch (e: any) {
    toast.error("Erro: " + e.message)
  } finally {
    downloading.value = false
  }
}

async function importAgents() {
  if (!importFile.value) return
  try {
    importing.value = true
    const text = await importFile.value.text()
    const pkg = JSON.parse(text)

    const res = await fetch(`${API}/agents/import`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pkg.agents || pkg),
    })
    if (!res.ok) throw new Error("Falha no import")
    const data = await res.json()
    toast.success(`Importação concluída! Criados: ${data.stats.created}, Atualizados: ${data.stats.updated}`)
  } catch (e: any) {
    toast.error("Erro: " + e.message)
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <div class="export-import-card">
    <h2>Exportar / Importar Agentes</h2>

    <div class="actions">
      <button :disabled="downloading" @click="downloadAgents">
        {{ downloading ? "Baixando..." : "Exportar (JSON)" }}
      </button>
    </div>

    <div class="actions">
      <input
        type="file"
        accept="application/json"
        @change="(e:any) => importFile.value = e.target.files?.[0] || null"
      />
      <button :disabled="importing || !importFile" @click="importAgents">
        {{ importing ? "Importando..." : "Importar JSON" }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.export-import-card {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
  background: #f9fafb;
}
.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  align-items: center;
}
button {
  padding: 8px 14px;
  background: #111827;
  color: #fff;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
