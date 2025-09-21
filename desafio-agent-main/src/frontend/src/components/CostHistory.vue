<script setup lang="ts">
import { storeToRefs } from "pinia"
import { useAgentRunnerStore } from "../stores/agentRunnerStore"

const store = useAgentRunnerStore()
const { costSummary, costDetails } = storeToRefs(store)

function formatCurrency(value: number) {
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  })
}
</script>

<template>
  <div v-if="costSummary.executions > 0" class="cost-history">
    <h3>💰 Histórico de Custos</h3>

    <div class="summary">
      <p><strong>Total gasto:</strong> {{ formatCurrency(costSummary.total_cost) }}</p>
      <p><strong>Média por execução:</strong> {{ formatCurrency(costSummary.average_cost) }}</p>
      <p><strong>Execuções:</strong> {{ costSummary.executions }}</p>
    </div>

    <div v-if="costSummary.by_provider && Object.keys(costSummary.by_provider).length > 0" class="providers">
      <p><strong>Por Provedor:</strong></p>
      <ul>
        <li v-for="(value, provider) in costSummary.by_provider" :key="provider">
          {{ provider }} → {{ formatCurrency(value) }}
        </li>
      </ul>
    </div>

    <div class="details">
      <h4>Detalhes das execuções</h4>
      <table v-if="costDetails.length > 0">
        <thead>
          <tr>
            <th>Execução</th>
            <th>Custo</th>
            <th>Data</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in costDetails" :key="c.execution_id">
            <td>#{{ c.execution_id }}</td>
            <td>{{ formatCurrency(c.cost) }}</td>
            <td>{{ new Date(c.created_at).toLocaleString("pt-BR") }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="no-details">Nenhum detalhe disponível.</p>
    </div>
  </div>
</template>

<style scoped>
.cost-history {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 6px;
}
.cost-history table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}
.cost-history th, .cost-history td {
  padding: 6px 10px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}
</style>