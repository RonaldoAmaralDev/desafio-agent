import { createRouter, createWebHistory } from "vue-router";
import PromptManager from "../components/PromptManager.vue";
import AgentRunner from "../components/AgentRunner.vue";
import AgentExportImport from "../components/AgentExportImport.vue";

const routes = [
  { path: "/", redirect: "/prompts" },
  { path: "/prompts", component: PromptManager },
  { path: "/agents/run", component: AgentRunner },
  { path: "/agents/import-export", component: AgentExportImport },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});