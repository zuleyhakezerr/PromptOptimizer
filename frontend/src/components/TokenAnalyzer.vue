<template>
  <div class="card p-6 space-y-6">
    <h2 class="text-2xl font-bold">Token Analizi</h2>
    
    <!-- Token Isı Haritası -->
    <div class="visualization-card">
      <h3 class="text-lg font-medium mb-4">Token Önem Skorları</h3>
      <div ref="heatmapContainer" class="h-64"></div>
    </div>
    
    <!-- Değişiklik Akış Diyagramı -->
    <div class="visualization-card">
      <h3 class="text-lg font-medium mb-4">Token Değişiklikleri</h3>
      <div ref="sankeyContainer" class="h-96"></div>
    </div>
    
    <!-- Metrikler Radar Grafiği -->
    <div class="visualization-card">
      <h3 class="text-lg font-medium mb-4">Optimizasyon Metrikleri</h3>
      <div ref="radarContainer" class="h-80"></div>
    </div>
    
    <!-- Önem Dağılımı -->
    <div class="visualization-card">
      <h3 class="text-lg font-medium mb-4">Token Önem Dağılımı</h3>
      <div ref="distributionContainer" class="h-64"></div>
    </div>
    
    <!-- Değişiklik Listesi -->
    <div class="visualization-card">
      <h3 class="text-lg font-medium mb-4">Değişiklik Detayları</h3>
      <div class="space-y-2">
        <div
          v-for="(change, index) in changes"
          :key="index"
          class="p-3 bg-gray-50 rounded-lg dark:bg-gray-800"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="text-red-500 line-through">{{ change.original }}</span>
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
              <span class="text-green-500">{{ change.optimized }}</span>
            </div>
            <span class="text-sm text-gray-500">
              Pozisyon: {{ change.position }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Güven Skoru -->
    <div class="visualization-card">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-medium">Güven Skoru</h3>
        <div class="flex items-center space-x-2">
          <div class="w-32 h-2 bg-gray-200 rounded-full">
            <div
              class="h-full rounded-full transition-all duration-300"
              :class="confidenceClass"
              :style="{ width: `${confidenceScore * 100}%` }"
            ></div>
          </div>
          <span class="text-sm font-medium">
            {{ (confidenceScore * 100).toFixed(1) }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted, computed, nextTick } from 'vue'
import Plotly from 'plotly.js-dist-min'
import type { Layout, Config } from 'plotly.js-dist'

interface TokenChange {
  original: string
  optimized: string
  position: number
  type: string
}

interface TokenImportance {
  [key: string]: number
}

interface Props {
  tokenImportance: TokenImportance
  changes: TokenChange[]
  confidenceScore: number
  visualizations: boolean
}

interface PlotData {
  type: string
  x?: (string | number)[]
  y?: (string | number)[]
  z?: (number | number[])[]
  text?: string | string[] | string[][]
  mode?: string
  name?: string
  colorscale?: Array<[number, string]>
  showscale?: boolean
  hoverongaps?: boolean
  texttemplate?: string
  textfont?: {
    size?: number
    color?: string
  }
  marker?: {
    color?: string
    line?: {
      color?: string
      width?: number
    }
  }
  line?: {
    color?: string
    width?: number
  }
  fill?: string
  fillcolor?: string
  hovertemplate?: string
  hoverlabel?: {
    bgcolor?: string
    font?: {
      color?: string
    }
  }
  node?: {
    pad?: number
    thickness?: number
    line?: {
      color?: string
      width?: number
    }
    label?: string[]
    color?: string[]
    hoverongaps?: boolean
    hoverlabel?: {
      bgcolor?: string
      font?: {
        color?: string
      }
    }
  }
  link?: {
    source?: number[]
    target?: number[]
    value?: number[]
    color?: string[]
    hovertemplate?: string
  }
  r?: number[]
  theta?: string[]
  orientation?: 'h' | 'v'
  nbinsx?: number
}

const props = defineProps<Props>()

// Container refs
const heatmapContainer = ref<HTMLElement | null>(null)
const sankeyContainer = ref<HTMLElement | null>(null)
const radarContainer = ref<HTMLElement | null>(null)
const distributionContainer = ref<HTMLElement | null>(null)

// Computed
const confidenceClass = computed(() => {
  const score = calculateOptimizationScore()
  if (score >= 0.8) return 'bg-green-500'
  if (score >= 0.5) return 'bg-yellow-500'
  return 'bg-red-500'
})

// Optimizasyon skorunu hesapla
const calculateOptimizationScore = () => {
  if (!props.tokenImportance || !props.changes) return 0

  // Token önem skorlarının ortalaması ve maksimumu
  const importanceScores = Object.values(props.tokenImportance)
  const maxImportance = Math.max(...importanceScores)
  const avgImportance = importanceScores.length > 0 
    ? importanceScores.reduce((a, b) => a + b, 0) / importanceScores.length 
    : 0
  const normalizedAvgImportance = avgImportance / maxImportance // 0-1 arası normalize et

  // Değişiklik oranı ve etkisi
  const changeRatio = Math.min(props.changes.length / Object.keys(props.tokenImportance).length, 1)
  const positiveChanges = props.changes.filter(change => {
    const originalScore = props.tokenImportance[change.original] || 0
    const optimizedScore = props.tokenImportance[change.optimized] || 0
    return optimizedScore > originalScore
  }).length
  const changeQuality = props.changes.length > 0 
    ? positiveChanges / props.changes.length 
    : 0

  // Önemli tokenlerin korunma oranı
  const importantTokens = new Set(
    Object.entries(props.tokenImportance)
      .filter(([, score]) => score > maxImportance * 0.7) // En yüksek skorun %70'inden fazla olanlar
      .map(([token]) => token)
  )
  const preservedImportantTokens = props.changes.filter(change =>
    !importantTokens.has(change.original) || importantTokens.has(change.optimized)
  ).length
  const preservationScore = props.changes.length > 0
    ? preservedImportantTokens / props.changes.length
    : 1

  // Ağırlıklı ortalama
  const weights = {
    confidence: 0.3,    // Güven skoru
    importance: 0.25,   // Önem skoru
    change: 0.2,       // Değişiklik oranı
    quality: 0.15,     // Değişiklik kalitesi
    preservation: 0.1   // Korunma oranı
  }

  const score = (props.confidenceScore * weights.confidence) +
                (normalizedAvgImportance * weights.importance) +
                (changeRatio * weights.change) +
                (changeQuality * weights.quality) +
                (preservationScore * weights.preservation)

  return Math.min(Math.max(score, 0), 1) // 0-1 arası normalize et
}

// Metrikleri hesapla
const calculateMetrics = () => {
  const scores = Object.values(props.tokenImportance)
  const maxScore = Math.max(...scores)
  
  // Güven skoru (model tarafından sağlanan)
  const confidenceScore = props.confidenceScore

  // Önem skoru (en yüksek önem skorlarının ortalaması)
  const sortedScores = [...scores].sort((a, b) => b - a)
  const topScoresCount = Math.max(3, Math.floor(scores.length * 0.2))
  const topScores = sortedScores.slice(0, topScoresCount)
  const importanceScore = topScores.length > 0 
    ? (topScores.reduce((a, b) => a + b, 0) / topScores.length) / maxScore
    : 0

  // Değişim skoru (optimal değişiklik oranı)
  const optimalChangeRatio = 0.3 // Hedef değişiklik oranı
  const actualChangeRatio = scores.length > 0 
    ? props.changes.length / scores.length
    : 0
  const changeScore = Math.max(0, 1 - Math.abs(optimalChangeRatio - actualChangeRatio) / optimalChangeRatio)

  // Kalite skoru (pozitif değişikliklerin oranı ve etkisi)
  const positiveChanges = props.changes.filter(change => {
    const originalScore = props.tokenImportance[change.original] || 0
    const optimizedScore = props.tokenImportance[change.optimized] || 0
    return optimizedScore > originalScore * 1.1 // En az %10 iyileşme
  })
  const qualityScore = props.changes.length > 0
    ? positiveChanges.length / props.changes.length
    : 0

  // Korunma skoru (önemli tokenlerin korunma oranı)
  const importantTokens = new Set(
    Object.entries(props.tokenImportance)
      .filter(([, score]) => score > maxScore * 0.7)
      .map(([token]) => token)
  )
  const preservedTokens = props.changes.filter(change =>
    !importantTokens.has(change.original) || importantTokens.has(change.optimized)
  ).length
  const preservationScore = props.changes.length > 0
    ? preservedTokens / props.changes.length
    : 1

  return {
    confidenceScore,
    importanceScore,
    changeScore,
    qualityScore,
    preservationScore
  }
}

// Görselleştirmeleri oluştur
const createVisualizations = () => {
  if (props.visualizations) {
    console.log('Token Importance:', props.tokenImportance)
    console.log('Changes:', props.changes)
    console.log('Confidence Score:', props.confidenceScore)

    // Isı haritası için veri hazırla
    const tokens = Object.keys(props.tokenImportance)
    const scores = Object.values(props.tokenImportance)
    
    // Boş veri kontrolü
    if (tokens.length === 0 || scores.length === 0) {
      console.warn('No token importance data available')
      return
    }

    const maxScore = Math.max(...scores)
    const normalizedScores = scores.map(score => score / maxScore)

    console.log('Heatmap Data:', {
      tokens,
      scores,
      maxScore,
      normalizedScores
    })

    // Isı haritası
    if (heatmapContainer.value) {
      const heatmapData: Partial<PlotData>[] = [{
        type: 'heatmap',
        z: [normalizedScores],
        x: tokens,
        y: ['Önem'],
        colorscale: [
          [0, '#fee2e2'],    // En düşük: Açık kırmızı
          [0.2, '#fecaca'],  // Düşük: Orta açık kırmızı
          [0.4, '#f87171'],  // Orta düşük: Koyu kırmızı
          [0.6, '#60a5fa'],  // Orta yüksek: Mavi
          [0.8, '#34d399'],  // Yüksek: Açık yeşil
          [1, '#059669']     // En yüksek: Koyu yeşil
        ],
        showscale: true,
        hoverongaps: false,
        text: [scores.map(score => score.toFixed(3))],
        hovertemplate: '<b>Token:</b> %{x}<br><b>Önem:</b> %{text}<extra></extra>',
        texttemplate: '%{text}',
        textfont: {
          size: 10,
          color: 'white'
        }
      }]
      const heatmapLayout: Partial<Layout> = {
        title: {
          text: 'Token Önem Skorları',
          font: { size: 16, color: '#374151' }
        },
        height: 200,
        margin: { t: 40, b: 50, l: 50, r: 30 },
        xaxis: { 
          title: 'Tokenlar',
          tickangle: -45,
          tickfont: { size: 10 }
        },
        yaxis: { title: 'Önem' },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#718096' }
      }
      const config: Partial<Config> = {
        responsive: true,
        displayModeBar: false
      }
      Plotly.newPlot(heatmapContainer.value, heatmapData, heatmapLayout, config)
    }
    
    // Sankey diyagramı için veri hazırla
    if (sankeyContainer.value && props.changes.length > 0) {
      const allTokens = [...new Set([
        ...props.changes.map(c => c.original),
        ...props.changes.map(c => c.optimized)
      ])]
      
      // Token önemine göre renk paleti
      const getTokenColor = (token: string) => {
        const score = props.tokenImportance[token] || 0
        if (score >= 0.8) return '#059669'      // Koyu yeşil
        if (score >= 0.6) return '#34d399'      // Açık yeşil
        if (score >= 0.4) return '#60a5fa'      // Mavi
        if (score >= 0.2) return '#f87171'      // Orta kırmızı
        return '#fecaca'                        // Açık kırmızı
      }

      const nodeColors = allTokens.map(getTokenColor)

      const sankeyData: Partial<PlotData>[] = [{
        type: 'sankey',
        orientation: 'h',
        node: {
          pad: 15,
          thickness: 20,
          line: { color: '#1f2937', width: 0.5 },
          label: allTokens.map(token => `${token} (${(props.tokenImportance[token] || 0).toFixed(2)})`),
          color: nodeColors,
          hoverongaps: false,
          hoverlabel: {
            bgcolor: '#1f2937',
            font: { color: 'white' }
          }
        },
        link: {
          source: props.changes.map((_, i) => i),
          target: props.changes.map((_, i) => i + props.changes.length),
          value: props.changes.map(change => 
            Math.abs(
              (props.tokenImportance[change.optimized] || 0) - 
              (props.tokenImportance[change.original] || 0)
            ) * 10 + 1
          ),
          color: props.changes.map(change => {
            const originalScore = props.tokenImportance[change.original] || 0
            const optimizedScore = props.tokenImportance[change.optimized] || 0
            const scoreDiff = optimizedScore - originalScore
            
            if (scoreDiff > 0.2) return 'rgba(5, 150, 105, 0.4)'
            if (scoreDiff > 0) return 'rgba(52, 211, 153, 0.4)'
            if (scoreDiff > -0.2) return 'rgba(96, 165, 250, 0.4)'
            if (scoreDiff > -0.4) return 'rgba(248, 113, 113, 0.4)'
            return 'rgba(254, 202, 202, 0.4)'
          }),
          hovertemplate: 
            'Değişiklik:<br>' +
            'Önceki: %{source.label}<br>' +
            'Sonraki: %{target.label}<br>' +
            '<extra></extra>'
        }
      }]
      
      const sankeyLayout: Partial<Layout> = {
        title: {
          text: 'Token Değişiklikleri',
          font: { size: 16, color: '#374151' }
        },
        height: 400,
        margin: { t: 40, b: 30, l: 30, r: 30 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#718096' }
      }
      
      const config: Partial<Config> = {
        responsive: true,
        displayModeBar: false
      }
      
      Plotly.newPlot(sankeyContainer.value, sankeyData, sankeyLayout, config)
    }
    
    // Radar grafik
    if (radarContainer.value) {
      const metrics = calculateMetrics()
      console.log('Metrics:', metrics)
      const radarData: Partial<PlotData>[] = [{
        type: 'scatterpolar',
        r: [
          metrics.confidenceScore,
          metrics.importanceScore,
          metrics.changeScore,
          metrics.qualityScore,
          metrics.preservationScore
        ],
        theta: [
          'Güven',
          'Önem',
          'Değişim',
          'Kalite',
          'Korunma'
        ],
        fill: 'toself',
        name: 'Metrikler',
        line: { color: '#22c55e' },
        fillcolor: 'rgba(34, 197, 94, 0.2)'
      }]
      
      const radarLayout: Partial<Layout> = {
        polar: {
          radialaxis: {
            visible: true,
            range: [0, 1],
            tickformat: '.0%'
          }
        },
        showlegend: false,
        title: 'Optimizasyon Metrikleri',
        margin: { t: 30, b: 30, l: 30, r: 30 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#718096' }
      }
      
      const config: Partial<Config> = {
        responsive: true,
        displayModeBar: false
      }
      
      Plotly.newPlot(radarContainer.value, radarData, radarLayout, config)
    }
    
    // Dağılım grafiği
    if (distributionContainer.value) {
      console.log('Distribution Data:', {
        scores,
        maxScore,
        binCount: Math.min(20, Math.ceil(Math.sqrt(scores.length)))
      })
      const distData: Partial<PlotData>[] = [{
        type: 'histogram',
        x: scores,
        nbinsx: Math.min(20, Math.ceil(Math.sqrt(scores.length))), // Optimal bin sayısı
        name: 'Önem Skorları',
        marker: {
          color: 'rgba(34, 197, 94, 0.6)',
          line: {
            color: '#22c55e',
            width: 1
          }
        },
        hovertemplate: 'Önem: %{x:.3f}<br>Sayı: %{y}<extra></extra>'
      }]
      
      const distLayout: Partial<Layout> = {
        title: 'Token Önem Dağılımı',
        xaxis: { 
          title: 'Önem Skoru',
          tickformat: '.2f',
          range: [0, maxScore * 1.1] // Maksimum değerin %10 üstüne kadar göster
        },
        yaxis: { 
          title: 'Token Sayısı',
          tickformat: 'd' // Tam sayı formatı
        },
        height: 300,
        margin: { t: 30, b: 50, l: 50, r: 30 },
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#718096' },
        bargap: 0.1
      }
      
      const config: Partial<Config> = {
        responsive: true,
        displayModeBar: false
      }
      
      Plotly.newPlot(distributionContainer.value, distData, distLayout, config)
    }
  }
}

// Görselleştirmeleri güncelle
watch(() => props.visualizations, () => {
  nextTick(() => {
    createVisualizations()
  })
}, { deep: true })

// Pencere boyutu değişikliklerini izle
let resizeTimeout: number
const handleResize = () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(() => {
    createVisualizations()
  }, 250)
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  nextTick(() => {
    createVisualizations()
  })
})

// Görselleştirmeleri temizle
const cleanupVisualizations = () => {
  if (heatmapContainer.value) {
    Plotly.purge(heatmapContainer.value)
  }
  if (sankeyContainer.value) {
    Plotly.purge(sankeyContainer.value)
  }
  if (radarContainer.value) {
    Plotly.purge(radarContainer.value)
  }
  if (distributionContainer.value) {
    Plotly.purge(distributionContainer.value)
  }
}

// Component unmount olduğunda görselleştirmeleri temizle
onUnmounted(() => {
  cleanupVisualizations()
})
</script>

<style scoped>
.visualization-card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow p-4;
}

.card {
  @apply bg-white dark:bg-gray-800 rounded-lg shadow-lg;
}
</style> 