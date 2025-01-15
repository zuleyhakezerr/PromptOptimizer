<template>
  <div class="card p-6 space-y-4">
    <h2 class="text-2xl font-bold">Prompt Karşılaştırması</h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Orijinal Prompt -->
      <div class="space-y-2">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Orijinal Prompt
        </h3>
        <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
          <p class="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
            {{ originalPrompt }}
          </p>
          <div class="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400">
            <span class="mr-2">{{ originalTokenCount }} token</span>
            <span>${{ originalCost.toFixed(6) }}</span>
          </div>
        </div>
      </div>
      
      <!-- Optimize Edilmiş Prompt -->
      <div class="space-y-2">
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100">
          Optimize Edilmiş Prompt
        </h3>
        <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
          <p class="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
            {{ optimizedPrompt }}
          </p>
          <div class="mt-2 flex items-center text-sm text-gray-500 dark:text-gray-400">
            <span class="mr-2">{{ optimizedTokenCount }} token</span>
            <span>${{ optimizedCost.toFixed(6) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Metrikler -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Token Tasarrufu -->
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Token Tasarrufu
        </h4>
        <p class="mt-1 text-2xl font-semibold">
          {{ tokenSavings }}%
        </p>
        <div class="mt-1 w-full h-2 bg-gray-200 rounded-full">
          <div
            class="h-full bg-green-500 rounded-full"
            :style="{ width: `${tokenSavings}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Maliyet Tasarrufu -->
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Maliyet Tasarrufu
        </h4>
        <p class="mt-1 text-2xl font-semibold">
          {{ costSavings }}%
        </p>
        <div class="mt-1 w-full h-2 bg-gray-200 rounded-full">
          <div
            class="h-full bg-blue-500 rounded-full"
            :style="{ width: `${costSavings}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Anlamsal Benzerlik -->
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Anlamsal Benzerlik
        </h4>
        <p class="mt-1 text-2xl font-semibold">
          {{ (semanticSimilarity * 100).toFixed(1) }}%
        </p>
        <div class="mt-1 w-full h-2 bg-gray-200 rounded-full">
          <div
            class="h-full rounded-full"
            :class="getSimilarityClass"
            :style="{ width: `${semanticSimilarity * 100}%` }"
          ></div>
        </div>
      </div>
      
      <!-- Optimizasyon Skoru -->
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Optimizasyon Skoru
        </h4>
        <p class="mt-1 text-2xl font-semibold">
          {{ (optimizationScore * 100).toFixed(1) }}%
        </p>
        <div class="mt-1 w-full h-2 bg-gray-200 rounded-full">
          <div
            class="h-full rounded-full"
            :class="getScoreClass"
            :style="{ width: `${optimizationScore * 100}%` }"
          ></div>
        </div>
      </div>
    </div>
    
    <!-- Değişiklik Detayları -->
    <div class="space-y-2">
      <h3 class="text-lg font-medium">Değişiklik Detayları</h3>
      <div class="comparison-view" ref="diffContainer">
        <!-- Plotly.js ile değişiklik görselleştirmesi burada oluşturulacak -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import Plotly from 'plotly.js-dist-min'

interface Props {
  originalPrompt: string
  optimizedPrompt: string
  originalTokenCount: number
  optimizedTokenCount: number
  originalCost: number
  optimizedCost: number
  semanticSimilarity: number
  optimizationScore: number
}

const props = defineProps<Props>()

const diffContainer = ref<HTMLElement | null>(null)

const tokenSavings = computed(() => {
  if (!props.originalTokenCount || !props.optimizedTokenCount) return 0
  const savings = ((props.originalTokenCount - props.optimizedTokenCount) / props.originalTokenCount) * 100
  return Math.max(0, Math.round(savings))
})

const costSavings = computed(() => {
  if (!props.originalCost || !props.optimizedCost) return 0
  const savings = ((props.originalCost - props.optimizedCost) / props.originalCost) * 100
  return Math.max(0, Math.round(savings))
})

const getSimilarityClass = computed(() => {
  if (!props.semanticSimilarity) return 'bg-gray-500'
  if (props.semanticSimilarity >= 0.8) return 'bg-green-500'
  if (props.semanticSimilarity >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
})

const getScoreClass = computed(() => {
  if (!props.optimizationScore) return 'bg-gray-500'
  if (props.optimizationScore >= 0.8) return 'bg-green-500'
  if (props.optimizationScore >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
})

const createDiffVisualization = () => {
  if (!diffContainer.value) return
  
  const originalWords = props.originalPrompt.split(' ')
  const optimizedWords = props.optimizedPrompt.split(' ')
  
  const trace1 = {
    y: originalWords,
    name: 'Orijinal',
    type: 'bar',
    orientation: 'h',
    marker: {
      color: 'rgba(55, 125, 255, 0.5)',
    },
  }
  
  const trace2 = {
    y: optimizedWords,
    name: 'Optimize Edilmiş',
    type: 'bar',
    orientation: 'h',
    marker: {
      color: 'rgba(16, 185, 129, 0.5)',
    },
  }
  
  const layout = {
    barmode: 'group',
    height: Math.max(originalWords.length, optimizedWords.length) * 25 + 100,
    margin: { l: 150, r: 50, t: 50, b: 50 },
    yaxis: {
      title: 'Kelimeler',
    },
    xaxis: {
      title: 'Token Sayısı',
    },
    showlegend: true,
    legend: {
      x: 0,
      y: 1.1,
    },
    plot_bgcolor: 'transparent',
    paper_bgcolor: 'transparent',
  }
  
  Plotly.newPlot(diffContainer.value, [trace1, trace2], layout)
}

onMounted(() => {
  createDiffVisualization()
  window.addEventListener('resize', createDiffVisualization)
})

onUnmounted(() => {
  window.removeEventListener('resize', createDiffVisualization)
})
</script> 