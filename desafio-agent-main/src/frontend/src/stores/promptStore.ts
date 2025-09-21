import { defineStore } from "pinia";
import { ref } from "vue";
import { useToast } from "vue-toastification";

const API_PROMPTS = import.meta.env.VITE_API_URL + "/prompts";

export const usePromptStore = defineStore("promptStore", () => {
  const prompts = ref<any[]>([]);
  const loading = ref(false);
  const toast = useToast();

  async function fetchPrompts() {
    try {
      loading.value = true;
      const res = await fetch(API_PROMPTS);
      if (!res.ok) throw new Error("Erro ao buscar prompts");
      prompts.value = await res.json();
    } catch (err: any) {
      toast.error("Erro ao buscar prompts: " + err.message);
    } finally {
      loading.value = false;
    }
  }

  async function createPrompt(prompt: any) {
    try {
      const res = await fetch(API_PROMPTS, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(prompt),
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Erro ao criar prompt");
      }
      const data = await res.json();
      prompts.value.push(data);
      toast.success("Prompt criado com sucesso!");
      return data;
    } catch (err: any) {
      toast.error("Erro ao criar prompt: " + err.message);
      throw err;
    }
  }

  return {
    prompts,
    loading,
    fetchPrompts,
    createPrompt,
  };
});