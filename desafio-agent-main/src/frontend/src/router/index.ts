import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router"

const PromptManager = () => import("../components/PromptManager.vue")
const AgentRunner = () => import("../components/AgentRunner.vue")
const AgentExportImport = () => import("../components/AgentExportImport.vue")
const NotFound = () => import("../components/NotFound.vue")

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/prompts",
  },
  {
    path: "/prompts",
    name: "Prompts",
    component: PromptManager,
    meta: { title: "Gestão de Prompts" },
  },
  {
    path: "/agents/run",
    name: "AgentRunner",
    component: AgentRunner,
    meta: { title: "Executar Agente" },
  },
  {
    path: "/agents/import-export",
    name: "AgentExportImport",
    component: AgentExportImport,
    meta: { title: "Importação & Exportação de Agentes" },
  },
  { path: "/:pathMatch(.*)*", name: "NotFound", component: NotFound, meta: { title: "Página não encontrada" } }

]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  if (to.meta?.title) {
    document.title = `${to.meta.title} | Agent Management Platform`
  }
})

export default router