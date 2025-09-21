<template>
  <div id="app">
    <header class="app-header">
      <div class="logo">🤖 Agent Management Platform</div>
      <nav class="nav-links">
        <router-link to="/prompts" class="nav-link" active-class="active-link">
          Prompts
        </router-link>
        <router-link to="/agents/run" class="nav-link" active-class="active-link">
          Executar Agente
        </router-link>
        <router-link to="/agents/import-export" class="nav-link" active-class="active-link">
          Importação & Exportação
        </router-link>
      </nav>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>© 2025 Agent Management Platform • Desenvolvido para desafio técnico</p>
    </footer>
  </div>
</template>

<script setup>
// NADA
</script>