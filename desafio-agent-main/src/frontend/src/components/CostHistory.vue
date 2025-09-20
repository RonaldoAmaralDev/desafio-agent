<template>
  <div v-if="summary.executions > 0" class="cost-history">
    <h3>💰 Histórico de Custos</h3>
    <p><strong>Total gasto:</strong> {{ formatCurrency(summary.total_cost) }}</p>
    <p><strong>Média por execução:</strong> {{ formatCurrency(summary.average_cost) }}</p>
    <p><strong>Execuções:</strong> {{ summary.executions }}</p>

    <table v-if="details.length > 0">
      <thead>
        <tr>
          <th>Execução</th>
          <th>Custo</th>
          <th>Data</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in details" :key="c.execution_id">
          <td>{{ c.execution_id }}</td>
          <td>{{ formatCurrency(c.cost) }}</td>
          <td>{{ new Date(c.created_at).toLocaleString("pt-BR") }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { withDefaults, defineProps, toRefs } from "vue";

type Summary = { total_cost: number; average_cost: number; executions: number };
type Detail = { execution_id: number; agent_id?: number; cost: number; created_at: string };

const props = withDefaults(
  defineProps<{
    summary?: Summary;
    details?: Detail[];
  }>(),
  {
    summary: () => ({ total_cost: 0, average_cost: 0, executions: 0 }),
    details: () => [],
  }
);

const { summary, details } = toRefs(props);

function formatCurrency(value: number) {
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}
</script>

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