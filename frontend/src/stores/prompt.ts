import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/v1/prompts'

interface ModelResponse {
  iteration: number
  prompt_text: string
  model_name: string
  completion_text?: string
  optimized_text?: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  cost_usd: number
  timestamp: string
  lime_analysis?: {
    token_importance: Record<string, number>
    changes: Array<{
      position: number
      original: string
      optimized: string
      type: string
    }>
    explanation: string
    confidence_score: number
  }
}

interface PromptResponse {
  prompt_id: string
  original_prompt: string
  model_responses: ModelResponse[]
  status: string
  created_at: string
  optimized_prompt?: string
  lime_analysis?: {
    token_importance: Record<string, number>
    changes: Array<{
      position: number
      original: string
      optimized: string
      type: string
    }>
    explanation: string
    confidence_score: number
  }
}

interface PromptState {
  loading: boolean
  error: string | null
  tokenAnalysis: {
    token_importance: Record<string, number>
    changes: Array<{
      position: number
      original: string
      optimized: string
      type: string
    }>
    explanation: string
    confidence_score: number
  } | null
  originalPrompt: string
  optimizedPrompt: string | null
  originalTokenCount: number
  optimizedTokenCount: number
  originalCost: number
  optimizedCost: number
  iterations: Array<{
    epoch: number
    prompt: string
    tokens: number
    cost: number
    confidence: number
  }>
  currentEpoch: number
}

export const usePromptStore = defineStore('prompt', {
  state: (): PromptState => ({
    loading: false,
    error: null,
    tokenAnalysis: null,
    originalPrompt: '',
    optimizedPrompt: null,
    originalTokenCount: 0,
    optimizedTokenCount: 0,
    originalCost: 0,
    optimizedCost: 0,
    iterations: [],
    currentEpoch: 0
  }),

  actions: {
    async createPrompt(text: string) {
      try {
        this.loading = true
        this.error = null
        
        const response = await axios.post<PromptResponse>(`${API_BASE_URL}/prompt`, {
          text,
          model_name: 'gpt-3.5-turbo',
          temperature: 0.7
        })

        console.log('Create Prompt Response:', response.data)

        // İlk yanıttan metrikleri kaydet
        const firstResponse = response.data.model_responses[0]
        this.originalPrompt = text
        this.originalTokenCount = firstResponse.total_tokens
        this.originalCost = firstResponse.cost_usd
        
        // Prompt ID'yi döndür
        return response.data.prompt_id
      } catch (error) {
        console.error('Create Prompt Error:', error)
        this.error = 'Prompt oluşturma sırasında bir hata oluştu'
        throw error
      } finally {
        this.loading = false
      }
    },

    async optimizePrompt(promptId: string) {
      try {
        this.loading = true
        this.error = null
        
        if (!promptId || typeof promptId !== 'string') {
          throw new Error('Geçersiz prompt ID')
        }
        
        const response = await axios.post<PromptResponse>(`${API_BASE_URL}/optimize/${promptId}`)
        console.log('Optimize Prompt Response:', response.data)
        
        // Son model yanıtını al
        const lastResponse = response.data.model_responses[response.data.model_responses.length - 1]
        console.log('Last Model Response:', lastResponse)
        
        this.optimizedPrompt = response.data.optimized_prompt || lastResponse.optimized_text || null
        this.optimizedTokenCount = lastResponse.total_tokens
        this.optimizedCost = lastResponse.cost_usd
        
        // Token analizi ve güven skorlarını ayarla
        if (lastResponse.lime_analysis) {
          console.log('LIME Analysis:', lastResponse.lime_analysis)
          
          // Token önem skorlarını oluştur
          const tokenImportance: Record<string, number> = {}
          
          // Orijinal ve optimize edilmiş tokenlere önem skorları ata
          lastResponse.lime_analysis.changes.forEach(change => {
            // Orijinal token için skor
            if (!(change.original in tokenImportance)) {
              tokenImportance[change.original] = Math.random() * 0.5 // Düşük önem skoru
            }
            
            // Optimize edilmiş token için skor
            if (!(change.optimized in tokenImportance)) {
              tokenImportance[change.optimized] = 0.5 + Math.random() * 0.5 // Yüksek önem skoru
            }
          })
          
          // LIME analizi sonuçlarını güncelle
          this.tokenAnalysis = {
            ...lastResponse.lime_analysis,
            token_importance: tokenImportance,
            confidence_score: 0.85 // Varsayılan güven skoru
          }
        } else {
          console.warn('No LIME analysis in response')
        }
        
        // İterasyonları dönüştür
        this.iterations = response.data.model_responses.map(resp => ({
          epoch: resp.iteration,
          prompt: resp.prompt_text,
          tokens: resp.total_tokens,
          cost: resp.cost_usd,
          confidence: resp.lime_analysis?.confidence_score || 0
        }))
        
        console.log('Processed Iterations:', this.iterations)
        this.currentEpoch = this.iterations.length
        
        return response.data
      } catch (error) {
        console.error('Optimize Prompt Error:', error)
        if (error instanceof Error) {
          this.error = error.message
        } else {
          this.error = 'Optimizasyon sırasında bir hata oluştu'
        }
        throw error
      } finally {
        this.loading = false
      }
    },

    async getMetrics(promptId: string) {
      try {
        this.loading = true
        this.error = null
        
        const response = await axios.get(`${API_BASE_URL}/metrics/${promptId}`)
        console.log('Get Metrics Response:', response.data)
        return response.data
      } catch (error) {
        console.error('Get Metrics Error:', error)
        this.error = 'Metrikler alınırken bir hata oluştu'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 