import { defineStore } from "pinia"
import { ref } from "vue"
import { useToast } from "vue-toastification"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

export const useAgentStore = defineStore("agentStore", () => {
  const toast = useToast()
  const downloading = ref(false)
  const importing = ref(false)

  async function exportAgents() {
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

  async function importAgents(file: File) {
    if (!file) return
    if (file.type !== "application/json") {
      toast.error("Por favor, selecione um arquivo JSON válido.")
      return
    }

    try {
      importing.value = true
      const text = await file.text()
      const pkg = JSON.parse(text)

      const res = await fetch(`${API}/agents/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pkg.agents || pkg),
      })

      if (!res.ok) throw new Error("Falha no import")
      const data = await res.json()

      toast.success(
        `Importação concluída! Criados: ${data.stats.created}, Atualizados: ${data.stats.updated}`
      )
    } catch (e: any) {
      toast.error("Erro: " + e.message)
    } finally {
      importing.value = false
    }
  }

  return { downloading, importing, exportAgents, importAgents }
})
