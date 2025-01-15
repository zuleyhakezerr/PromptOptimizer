<template>
  <div class="card p-6">
    <h2 class="text-2xl font-bold mb-4">Model Seçimi</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- GPT-3.5 -->
      <button
        class="p-4 rounded-lg border-2 transition-all duration-200 flex flex-col items-center justify-center space-y-2"
        :class="[
          selectedModel === 'gpt-3.5-turbo' 
            ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
            : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
        ]"
        @click="selectModel('gpt-3.5-turbo')"
      >
        <div class="text-lg font-medium">GPT-3.5 Turbo</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Hızlı ve Ekonomik</div>
        <div class="text-xs text-gray-500 dark:text-gray-500">$0.002 / 1K token</div>
      </button>
      
      <!-- GPT-4 -->
      <button
        class="p-4 rounded-lg border-2 transition-all duration-200 flex flex-col items-center justify-center space-y-2"
        :class="[
          selectedModel === 'gpt-4' 
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
            : 'border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600'
        ]"
        @click="selectModel('gpt-4')"
      >
        <div class="text-lg font-medium">GPT-4</div>
        <div class="text-sm text-gray-600 dark:text-gray-400">Daha Yetenekli</div>
        <div class="text-xs text-gray-500 dark:text-gray-500">$0.03 / 1K token</div>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const selectedModel = ref('gpt-3.5-turbo')
const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
}>()

const selectModel = (modelId: string) => {
  selectedModel.value = modelId
  emit('update:modelId', modelId)
}
</script> 