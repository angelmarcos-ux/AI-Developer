import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface AnalysisResult {
  enquiry: string
  category: string
  priority: string
  sentiment: string
  confidence: number
  is_vague: boolean
  suggested_response: string
  recommended_actions: string[]
  reasoning: string
  timestamp?: string
}

export interface ApiAnalyseResponse {
  success: boolean
  data: Omit<AnalysisResult, 'enquiry' | 'timestamp'>
  enquiry: string
  timestamp: string
}

export interface ApiHistoryResponse {
  success: boolean
  data: ApiAnalyseResponse[]
}

export const useEnquiryStore = defineStore('enquiry', () => {
  const result = ref<AnalysisResult | null>(null)
  const history = ref<AnalysisResult[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function submitEnquiry(text: string): Promise<void> {
    loading.value = true
    error.value = null
    const config = useRuntimeConfig()

    try {
      const response = await $fetch<ApiAnalyseResponse>(`${config.public.apiBase}/analyse`, {
        method: 'POST',
        body: { enquiry: text }
      })
      result.value = {
        ...response.data,
        enquiry: response.enquiry,
        timestamp: response.timestamp,
      }
      await fetchHistory()
    } catch (err: any) {
      if (err?.data?.detail) {
         // FastAPI uses 'detail' for errors
         error.value = err.data.detail
      } else if (err?.response?.status === 429) {
        error.value = 'ERR: RATE_LIMIT_EXCEEDED - Maximum requests reached. Please wait before executing again.'
      } else if (err?.data?.error && typeof err.data.error === 'string') {
        error.value = err.data.error
      } else if (err?.statusMessage) {
        error.value = err.statusMessage
      } else if (err?.message) {
        error.value = err.message
      } else {
        error.value = 'An unexpected error occurred. Please try again.'
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchHistory(): Promise<void> {
    const config = useRuntimeConfig()
    try {
      const response = await $fetch<ApiHistoryResponse>(`${config.public.apiBase}/history`)
      history.value = response.data.map((entry: ApiAnalyseResponse) => ({
        ...entry.data,
        enquiry: entry.enquiry,
        timestamp: entry.timestamp,
      }))
    } catch (err: any) {
      console.error('Failed to fetch history:', err)
    }
  }

  function selectHistoryItem(item: AnalysisResult): void {
    result.value = item
  }

  return {
    result,
    history,
    loading,
    error,
    submitEnquiry,
    fetchHistory,
    selectHistoryItem
  }
})
