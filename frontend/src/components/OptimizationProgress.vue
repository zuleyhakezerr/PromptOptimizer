<template>
  <div class="card p-6 space-y-4">
    <h2 class="text-2xl font-bold">Optimizasyon İlerlemesi</h2>
    
    <div class="optimization-progress bg-white dark:bg-gray-800 p-4 rounded-lg shadow" ref="chartContainer">
      <h3 class="text-lg font-medium mb-4">İlerleme Grafiği</h3>
      <canvas></canvas>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Toplam Token
        </h3>
        <p class="mt-1 text-2xl font-semibold">
          {{ totalTokens }}
        </p>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
          Maliyet: ${{ totalCost.toFixed(6) }}
        </p>
      </div>
      
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          İterasyon Sayısı
        </h3>
        <p class="mt-1 text-2xl font-semibold">
          {{ currentEpoch }} / {{ totalEpochs }}
        </p>
        <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
          {{ ((currentEpoch / totalEpochs) * 100).toFixed(1) }}% Tamamlandı
        </p>
      </div>
      
      <div class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">
          Ortalama Güven Skoru
        </h3>
        <p class="mt-1 text-2xl font-semibold">
          {{ (averageConfidence * 100).toFixed(1) }}%
        </p>
        <div class="mt-1 w-full h-2 bg-gray-200 rounded-full">
          <div
            class="h-full rounded-full transition-all duration-500"
            :class="getConfidenceClass"
            :style="{ width: `${averageConfidence * 100}%` }"
          ></div>
        </div>
      </div>
    </div>
    
    <div class="space-y-2">
      <h3 class="text-lg font-medium">İterasyon Geçmişi</h3>
      <div class="space-y-2">
        <div
          v-for="(iteration, index) in iterations"
          :key="index"
          class="p-4 bg-gray-50 rounded-lg dark:bg-gray-900"
        >
          <div class="flex items-center justify-between">
            <span class="font-medium">İterasyon {{ iteration.epoch }}</span>
            <span
              class="px-2 py-1 text-sm rounded"
              :class="getScoreClass(iteration.confidence)"
            >
              {{ (iteration.confidence * 100).toFixed(1) }}% Güven
            </span>
          </div>
          
          <div class="mt-2 space-y-1">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Tokenlar: {{ iteration.tokens }}
            </p>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              Maliyet: ${{ iteration.cost.toFixed(6) }}
            </p>
            <p class="mt-2 text-gray-800 dark:text-gray-200">
              {{ iteration.prompt }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

interface Iteration {
  epoch: number
  prompt: string
  tokens: number
  cost: number
  confidence: number
}

interface Props {
  iterations: Iteration[]
  currentEpoch: number
  totalEpochs: number
}

const props = defineProps<Props>()

const chartContainer = ref<HTMLCanvasElement | null>(null)
let chart: Chart | null = null

const totalTokens = computed(() => 
  props.iterations.reduce((sum, iter) => sum + iter.tokens, 0)
)

const totalCost = computed(() =>
  props.iterations.reduce((sum, iter) => sum + iter.cost, 0)
)

const averageConfidence = computed(() =>
  props.iterations.length
    ? props.iterations.reduce((sum, iter) => sum + iter.confidence, 0) / props.iterations.length
    : 0
)

const getScoreClass = (score: number) => {
  if (score >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
  if (score >= 0.5) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
}

const getConfidenceClass = computed(() => {
  if (averageConfidence.value >= 0.8) return 'bg-green-500'
  if (averageConfidence.value >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
})

const createChart = () => {
  if (!chartContainer.value) return
  
  const canvas = chartContainer.value.querySelector('canvas')
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  if (chart) {
    chart.destroy()
  }
  
  const labels = props.iterations.map(iter => `İterasyon ${iter.epoch}`)
  const confidenceData = props.iterations.map(iter => iter.confidence * 100)
  const tokenData = props.iterations.map(iter => iter.tokens)
  
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Güven Skoru (%)',
          data: confidenceData,
          borderColor: '#10B981',
          backgroundColor: '#10B98120',
          yAxisID: 'y',
        },
        {
          label: 'Token Sayısı',
          data: tokenData,
          borderColor: '#6366F1',
          backgroundColor: '#6366F120',
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Güven Skoru (%)',
          },
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Token Sayısı',
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    },
  })
}

onMounted(() => {
  createChart()
  window.addEventListener('resize', createChart)
})

watch(() => props.iterations, createChart, { deep: true })

onUnmounted(() => {
  window.removeEventListener('resize', createChart)
  if (chart) {
    chart.destroy()
  }
})
</script>

<style scoped>
.optimization-progress {
  min-height: 300px;
}
</style> 