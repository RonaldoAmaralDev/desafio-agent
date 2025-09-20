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
          Importação & Exportação de Agente
        </router-link>
      </nav>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <p>© 2025 Agent Management Platform. Desenvolvido para desafio técnico.</p>
    </footer>
  </div>
</template>

<script setup>

</script>

<style scoped>
#app {
  font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333;
  display: flex;
  flex-direction: column;
  min-height: 98vh;
  background: #f5f7fa;
  margin: 0;
}

.app-header {
  background: #1e88e5;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 1.3rem;
  font-weight: bold;
}

.nav-links {
  display: flex;
  gap: 1.5rem;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #bbdefb;
}

.active-link {
  border-bottom: 2px solid #fff;
  padding-bottom: 2px;
}

.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.app-footer {
  background: #1e88e5;
  color: white;
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
}
</style>
