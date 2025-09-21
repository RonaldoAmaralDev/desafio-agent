<template>
  <div class="not-found">
    <h1>404 - Página não encontrada</h1>
    <p>A página que você tentou acessar não existe.</p>
    <router-link to="/" class="btn-home">Voltar para o início</router-link>
  </div>
</template>

<script setup>
// Nada
</script>

<style scoped>
.not-found {
  text-align: center;
  padding: 4rem 2rem;
}

.not-found h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #1e88e5;
}

.not-found p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.btn-home {
  display: inline-block;
  padding: 0.6rem 1.2rem;
  background: #1e88e5;
  color: white;
  font-weight: 500;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.2s;
}

.btn-home:hover {
  background: #1565c0;
}
</style>
