<template>
  <transition name="toast-fade">
    <div v-if="visible" :class="['toast', type]">
      {{ message }}
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, defineProps } from "vue";

const props = defineProps({
  message: { type: String, required: true },
  type: { type: String, default: "info" }, // info, success, error
  duration: { type: Number, default: 3000 } // ms
});

const visible = ref(false);

watch(
  () => props.message,
  (newVal) => {
    if (newVal) {
      visible.value = true;
      setTimeout(() => {
        visible.value = false;
      }, props.duration);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.toast {
  position: fixed;
  top: 80px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: black;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 1000;
}

/* tipos */
.toast.info {
  background-color: #2196f3;
}

.toast.success {
  background-color: #4caf50;
}

.toast.error {
  background-color: #f44336;
}

/* animação */
.toast-fade-enter-active, .toast-fade-leave-active {
  transition: opacity 0.3s;
}
.toast-fade-enter-from, .toast-fade-leave-to {
  opacity: 0;
}
</style>
