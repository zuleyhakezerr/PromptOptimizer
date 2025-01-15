export interface Iteration {
  epoch: number
  prompt: string
  tokens: number
  cost: number
  confidence: number
}

export interface OptimizationResult {
  optimizedPrompt: string
  optimizedTokenCount: number
  optimizedCost: number
  semanticSimilarity: number
  optimizationScore: number
  tokenImportance: Record<string, number>
  confidenceScores: Record<string, number>
  iterations: Iteration[]
  currentEpoch: number
  totalEpochs: number
} 