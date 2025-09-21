import { defineStore } from "pinia"
import { ref } from "vue"
import { useToast } from "vue-toastification"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"

export const useAgentRunnerStore = defineStore("agentRunnerStore", () => {
  const toast = useToast()

  const agents = ref<any[]>([])
  const selectedAgentId = ref<string>("")
  const question = ref<string>("")
  const answer = ref<string>("")
  const memory = ref<any[]>([])
  const agentInfo = ref<{ name: string; provider: string } | null>(null)

  // 💰 Custos
  const costSummary = ref({ total_cost: 0, average_cost: 0, executions: 0, by_provider: {} })
  const costDetails = ref<any[]>([])

  const loading = ref(false)

  async function fetchAgents() {
    try {
      const res = await fetch(`${API}/agents`)
      agents.value = await res.json()
      if (agents.value.length > 0) {
        selectedAgentId.value = agents.value[0].id
      }
    } catch (err: any) {
      toast.error("Erro ao carregar agentes: " + err.message)
    }
  }

  async function fetchCosts(agentId: string) {
    try {
      // Summary
      const resSummary = await fetch(`${API}/agents/${agentId}/costs/summary`)
      if (resSummary.ok) {
        costSummary.value = await resSummary.json()
      }

      // Details
      const resDetails = await fetch(`${API}/agents/${agentId}/costs`)
      if (resDetails.ok) {
        costDetails.value = await resDetails.json()
      }
    } catch (err: any) {
      toast.error("Erro ao buscar custos: " + err.message)
    }
  }

  async function askAgent() {
    if (!selectedAgentId.value || !question.value) return
    loading.value = true
    answer.value = ""
    memory.value = []
    agentInfo.value = null

    try {
      const res = await fetch(`${API}/agents/${selectedAgentId.value}/run/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: question.value })
      })

      if (!res.ok || !res.body) {
        const errorData = await res.json().catch(() => ({}))
        toast.error(errorData.detail || "Erro ao executar agente")
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""

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
            answer.value += msg.content
          }
          if (msg.type === "end") {
            answer.value = msg.answer
            memory.value = (msg.memory || []).map((m: any) => ({
              ...m,
              agent_name: msg.agent_name,
              provider: msg.provider
            }))
            agentInfo.value = { name: msg.agent_name, provider: msg.provider }
            toast.success("✅ Execução concluída!")
            await fetchCosts(selectedAgentId.value)
          }
        }
      }
    } catch (err: any) {
      toast.error("Erro: " + err.message)
    } finally {
      loading.value = false
    }
  }

  async function clearMemory() {
    if (!selectedAgentId.value) return
    loading.value = true
    try {
      const res = await fetch(`${API}/agents/${selectedAgentId.value}/memory`, {
        method: "DELETE"
      })
      if (!res.ok) throw new Error("Erro ao limpar memória")
      memory.value = []
      toast.success("Memória limpa com sucesso!")
    } catch (err: any) {
      toast.error("Erro: " + err.message)
    } finally {
      loading.value = false
    }
  }

  return {
    agents,
    selectedAgentId,
    question,
    answer,
    memory,
    agentInfo,
    costSummary,
    costDetails,
    loading,
    fetchAgents,
    fetchCosts,
    askAgent,
    clearMemory
  }
})
