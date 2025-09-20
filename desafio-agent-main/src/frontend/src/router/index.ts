import { createRouter, createWebHistory } from "vue-router";
import PromptManager from "../components/PromptManager.vue";
import AgentRunner from "../components/AgentRunner.vue";

const routes = [
  { path: "/", redirect: "/prompts" },
  { path: "/prompts", component: PromptManager },
  { path: "/agents/run", component: AgentRunner }
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});