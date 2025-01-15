<template>
  <main class="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Başlık -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-white">
          Prompt Optimizer
        </h1>
        <p class="mt-2 text-lg text-gray-600 dark:text-gray-400">
          LIME ile açıklanabilir prompt optimizasyonu
        </p>
      </div>

      <!-- Model Seçimi -->
      <ModelSelector v-model:modelId="selectedModel" />

      <!-- Prompt Girişi -->
      <div class="card p-6">
        <div class="space-y-4">
          <textarea
            v-model="prompt"
            class="w-full h-32 p-4 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            placeholder="Promptunuzu buraya girin..."
          ></textarea>
          
          <div class="flex justify-between items-center">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              {{ tokenCount }} token
            </div>
            
            <button
              class="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isOptimizing || !prompt"
              @click="optimizePrompt"
            >
              {{ isOptimizing ? 'Optimize Ediliyor...' : 'Optimize Et' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Yükleniyor -->
      <div v-if="store.loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Analiz yükleniyor...</p>
      </div>

      <!-- Hata -->
      <div v-else-if="store.error" class="bg-red-50 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 px-4 py-3 rounded-lg">
        <p class="font-medium">{{ store.error }}</p>
        <button
          @click="store.error = null"
          class="mt-2 text-sm text-red-600 dark:text-red-300 hover:text-red-800 dark:hover:text-red-100"
        >
          Tekrar Dene
        </button>
      </div>

      <!-- Analiz Sonuçları -->
      <div v-else-if="store.tokenAnalysis" class="space-y-8">
        <!-- Token Analizi -->
        <TokenAnalyzer
          :token-importance="store.tokenAnalysis.token_importance"
          :changes="store.tokenAnalysis.changes"
          :explanation="store.tokenAnalysis.explanation"
          :confidence-score="store.tokenAnalysis.confidence_score"
          :visualizations="visualizations as any"
        />

        <!-- Optimizasyon İlerlemesi -->
        <OptimizationProgress
          :iterations="store.iterations"
          :current-epoch="store.currentEpoch"
          :total-epochs="5"
        />

        <!-- Karşılaştırma Görünümü -->
        <ComparisonView
          v-if="store.optimizedPrompt"
          :original-prompt="store.originalPrompt"
          :optimized-prompt="store.optimizedPrompt"
          :original-token-count="store.originalTokenCount"
          :optimized-token-count="store.optimizedTokenCount"
          :original-cost="store.originalCost"
          :optimized-cost="store.optimizedCost"
          :semantic-similarity="0.85"
          :optimization-score="store.tokenAnalysis.confidence_score"
        />
      </div>

      <!-- Boş Durum -->
      <div v-else class="text-center py-12">
        <p class="text-gray-600 dark:text-gray-400">
          Optimize edilecek bir prompt girin ve başlayın.
        </p>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePromptStore } from '@/stores/prompt'
import TokenAnalyzer from '@/components/TokenAnalyzer.vue'
import OptimizationProgress from '@/components/OptimizationProgress.vue'
import ComparisonView from '@/components/ComparisonView.vue'
import ModelSelector from '@/components/ModelSelector.vue'
import type { Layout } from 'plotly.js'

// Özel tip tanımlamaları
interface BaseTrace {
  type: string
  name?: string
  hovertemplate?: string
}

interface HeatmapTrace extends BaseTrace {
  type: 'heatmap'
  z: number[][]
  x: string[]
  y?: string[]
  colorscale: string | Array<[number, string]>
  showscale: boolean
}

interface SankeyTrace extends BaseTrace {
  type: 'sankey'
  orientation: 'h' | 'v'
  node: {
    pad: number
    thickness: number
    line: { color: string; width: number }
    label: string[]
    color: string[]
  }
  link: {
    source: number[]
    target: number[]
    value: number[]
    color: string[]
  }
}

interface ScatterPolarTrace extends BaseTrace {
  type: 'scatterpolar'
  r: number[]
  theta: string[]
  fill: 'toself'
  name?: string
}

interface HistogramTrace extends BaseTrace {
  type: 'histogram'
  x: number[]
  nbinsx: number
  marker: {
    color: string
    line: {
      color: string
      width: number
    }
  }
}

type CustomPlotData = HeatmapTrace | SankeyTrace | ScatterPolarTrace | HistogramTrace

interface Visualization {
  data: CustomPlotData[]
  layout: Partial<Layout>
}

interface Visualizations {
  token_heatmap: Visualization
  changes_sankey: Visualization
  metrics_radar: Visualization
  importance_distribution: Visualization
}

const route = useRoute()
const store = usePromptStore()

const selectedModel = ref('gpt-3.5-turbo')
const prompt = ref('')
const isOptimizing = ref(false)

const tokenCount = computed(() => {
  return prompt.value.split(/\s+/).length
})

const optimizePrompt = async () => {
  isOptimizing.value = true
  try {
    // Önce prompt oluştur
    const promptId = await store.createPrompt(prompt.value)
    
    if (!promptId) {
      throw new Error('Prompt ID alınamadı')
    }

    // Sonra optimize et
    await store.optimizePrompt(promptId)
    
  } catch (error) {
    console.error('Optimizasyon hatası:', error)
  } finally {
    isOptimizing.value = false
  }
}

// TokenAnalyzer bileşeni için visualizations prop'unu ekle
const visualizations = computed<Visualizations>(() => {
  console.log('Store Token Analysis:', store.tokenAnalysis)
  console.log('Store Original Prompt:', store.originalPrompt)
  console.log('Store Optimized Prompt:', store.optimizedPrompt)
  console.log('Store Iterations:', store.iterations)

  const defaultVisualizations: Visualizations = {
    token_heatmap: {
      data: [{
        type: 'heatmap',
        z: [[0]],
        x: ['Veri Yok'],
        colorscale: 'RdYlBu',
        showscale: true
      }],
      layout: {
        title: 'Token Önem Skorları',
        height: 200,
        xaxis: { title: 'Tokenlar' },
        yaxis: { title: 'Önem' }
      }
    },
    changes_sankey: {
      data: [{
        type: 'sankey',
        orientation: 'h',
        node: {
          pad: 15,
          thickness: 20,
          line: { color: 'black', width: 0.5 },
          label: ['Başlangıç'],
          color: ['#48BB78']
        },
        link: {
          source: [0],
          target: [0],
          value: [1],
          color: ['#48BB78']
        }
      }],
      layout: {
        title: 'Token Değişiklikleri',
        height: 400
      }
    },
    metrics_radar: {
      data: [{
        type: 'scatterpolar',
        r: [0, 0, 0, 0, 0],
        theta: ['Güven', 'Önem', 'Değişim', 'Netlik', 'Anlamlılık'],
        fill: 'toself',
        name: 'Metrikler'
      }],
      layout: {
        polar: {
          radialaxis: {
            visible: true,
            range: [0, 1]
          }
        },
        showlegend: true,
        title: 'Optimizasyon Metrikleri'
      }
    },
    importance_distribution: {
      data: [{
        type: 'histogram',
        x: [0],
        nbinsx: 20,
        name: 'Önem Skorları',
        marker: {
          color: '#48BB78',
          line: {
            color: '#2F855A',
            width: 1
          }
        }
      }],
      layout: {
        title: 'Token Önem Dağılımı',
        xaxis: { title: 'Önem Skoru' },
        yaxis: { title: 'Token Sayısı' },
        height: 300
      }
    }
  }

  if (!store.tokenAnalysis) {
    console.log('No token analysis data available')
    return defaultVisualizations
  }
  
  // Token analizi varsa gerçek verileri kullan
  const tokenImportance = store.tokenAnalysis.token_importance
  const tokens = Object.keys(tokenImportance)
  const scores = Object.values(tokenImportance)
  const changes = store.tokenAnalysis.changes

  console.log('Visualization Data:', {
    tokenImportance,
    tokens,
    scores,
    changes
  })

  return {
    token_heatmap: {
      data: [{
        type: 'heatmap',
        z: [scores],
        x: tokens,
        colorscale: 'RdYlBu',
        showscale: true
      }],
      layout: {
        title: 'Token Önem Skorları',
        height: 200,
        xaxis: { title: 'Tokenlar' },
        yaxis: { title: 'Önem' }
      }
    },
    changes_sankey: {
      data: [{
        type: 'sankey',
        orientation: 'h',
        node: {
          pad: 15,
          thickness: 20,
          line: { color: 'black', width: 0.5 },
          label: [...new Set([...changes.map(c => c.original), ...changes.map(c => c.optimized)])],
          color: Array(changes.length * 2).fill('#48BB78')
        },
        link: {
          source: changes.map((_, i) => i),
          target: changes.map((_, i) => i + changes.length),
          value: changes.map(() => 1),
          color: Array(changes.length).fill('#48BB78')
        }
      }],
      layout: {
        title: 'Token Değişiklikleri',
        height: 400
      }
    },
    metrics_radar: {
      data: [{
        type: 'scatterpolar',
        r: [
          store.tokenAnalysis.confidence_score,
          scores.length > 0 ? Math.max(...scores) : 0,
          changes.length / tokens.length,
          0.8,
          0.9
        ],
        theta: ['Güven', 'Önem', 'Değişim', 'Netlik', 'Anlamlılık'],
        fill: 'toself',
        name: 'Metrikler'
      }],
      layout: {
        polar: {
          radialaxis: {
            visible: true,
            range: [0, 1]
          }
        },
        showlegend: true,
        title: 'Optimizasyon Metrikleri'
      }
    },
    importance_distribution: {
      data: [{
        type: 'histogram',
        x: scores,
        nbinsx: 20,
        name: 'Önem Skorları',
        marker: {
          color: '#48BB78',
          line: {
            color: '#2F855A',
            width: 1
          }
        }
      }],
      layout: {
        title: 'Token Önem Dağılımı',
        xaxis: { title: 'Önem Skoru' },
        yaxis: { title: 'Token Sayısı' },
        height: 300
      }
    }
  }
})

onMounted(async () => {
  // Sayfa yüklendiğinde mevcut promptId varsa analizi getir
  if (route.params.promptId) {
    try {
      await store.optimizePrompt(route.params.promptId as string)
    } catch (error) {
      console.error('Analiz yüklenirken hata:', error)
    }
  }
})
</script>
