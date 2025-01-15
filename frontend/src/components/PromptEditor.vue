<template>
  <div class="card p-6 space-y-4">
    <h2 class="text-2xl font-bold">Prompt Düzenleyici</h2>
    
    <div class="space-y-2">
      <label for="prompt" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Prompt Metni
      </label><textarea
        id="prompt"
        v-model="prompt"
        rows="4"
        class="input"
        placeholder="Promptunuzu buraya yazın..."
      ></textarea>
    </div>
    
    <div class="flex items-center space-x-4">
      <button
        @click="optimize"
        class="btn-primary"
        :disabled="isOptimizing"
      >
        <span v-if="isOptimizing" class="flex items-center">
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Optimize Ediliyor...
        </span>
        <span v-else>Optimize Et</span>
      </button>
      
      <button
        @click="reset"
        class="btn-secondary"
        :disabled="isOptimizing"
      >
        Sıfırla
      </button>
    </div>
    
    <div v-if="optimizedPrompt" class="space-y-2">
      <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
        Optimize Edilmiş Prompt
      </h3>
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <p class="text-gray-800 dark:text-gray-200">{{ optimizedPrompt }}</p>
      </div>
    </div>
    
    <div v-if="error" class="p-4 bg-red-50 text-red-700 rounded-lg dark:bg-red-900 dark:text-red-200">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { usePromptStore } from '@/stores/prompt'

const promptStore = usePromptStore()

const prompt = ref('')
const optimizedPrompt = ref('')
const isOptimizing = ref(false)
const error = ref('')

const optimize = async () => {
  if (!prompt.value.trim()) {
    error.value = 'Lütfen bir prompt girin.'
    return
  }
  
  try {
    isOptimizing.value = true
    error.value = ''
    
    const createResult = await promptStore.createPrompt(prompt.value)
    
    if (!createResult?.id) {
      throw new Error('Prompt ID alınamadı')
    }
    
    const result = await promptStore.optimizePrompt(createResult.id)
    optimizedPrompt.value = result.optimized_prompt
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Bir hata oluştu.'
  } finally {
    isOptimizing.value = false
  }
}

const reset = () => {
  prompt.value = ''
  optimizedPrompt.value = ''
  error.value = ''
}
</script> 