<script setup lang="ts">
import { useEnquiryStore } from '~/stores/enquiry'
import type { AnalysisResult } from '~/stores/enquiry'

const store = useEnquiryStore()

function getPriorityColor(priority: string): string {
  const p = priority?.toLowerCase()
  if (p === 'urgent') return 'text-red-500'
  if (p === 'high') return 'text-orange-500'
  if (p === 'medium') return 'text-yellow-500'
  return 'text-green-500'
}

function getSentimentIndicator(sentiment: string): string {
  const s = sentiment?.toLowerCase()
  if (s === 'positive') return '▲'
  if (s === 'negative') return '▼'
  return '▬'
}

function getSentimentColor(sentiment: string): string {
  const s = sentiment?.toLowerCase()
  if (s === 'positive') return 'text-green-500'
  if (s === 'negative') return 'text-red-500'
  return 'text-gray-500'
}

function formatTime(timestamp?: string): string {
  if (!timestamp) return '00:00:00'
  const date = new Date(timestamp)
  return date.toTimeString().split(' ')[0] // HH:MM:SS
}

function isActive(item: AnalysisResult): boolean {
  return store.result?.timestamp === item.timestamp && store.result?.enquiry === item.enquiry
}
</script>

<template>
  <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-0' } }" class="h-full flex flex-col">
    <template #header>
      <div class="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
        <div class="flex items-center gap-2">
          <UIcon name="i-heroicons-bars-3-bottom-left" class="w-5 h-5 text-primary-400" />
          <h2 class="text-sm font-mono font-semibold text-gray-200 uppercase tracking-wider">Transaction Ledger</h2>
        </div>
        <div class="flex items-center gap-2">
          <UBadge color="primary" variant="subtle" size="xs" class="font-mono">{{ store.history.length }} ENTRIES</UBadge>
          <UButton 
            v-if="store.history.length > 0"
            icon="i-heroicons-trash" 
            color="gray" 
            variant="ghost" 
            size="2xs" 
            @click.stop="store.history = []; store.result = null"
            title="Clear History"
          />
        </div>
      </div>
    </template>

    <div class="flex-1 overflow-y-auto max-h-[600px] bg-gray-950">
      <!-- Table Header -->
      <div class="grid grid-cols-12 gap-2 px-4 py-2 border-b border-gray-800 text-[10px] font-mono text-gray-500 uppercase tracking-wider sticky top-0 bg-gray-950 z-10">
        <div class="col-span-2">TIME</div>
        <div class="col-span-3">PRIORITY</div>
        <div class="col-span-4">CATEGORY</div>
        <div class="col-span-2 text-right">CONF</div>
        <div class="col-span-1 text-center">S</div>
      </div>

      <div v-if="!store.history.length" class="p-6 text-center text-xs font-mono text-gray-600">
        NO TRANSACTIONS FOUND
      </div>

      <div v-else class="divide-y divide-gray-800/50">
        <div
          v-for="(item, idx) in store.history"
          :key="idx"
          class="grid grid-cols-12 gap-2 px-4 py-2 text-xs font-mono cursor-pointer transition-colors hover:bg-gray-900"
          :class="[isActive(item) ? 'bg-primary-900/20 border-l-2 border-l-primary-500' : 'border-l-2 border-l-transparent']"
          @click="store.selectHistoryItem(item)"
        >
          <div class="col-span-2 text-gray-400">{{ formatTime(item.timestamp) }}</div>
          <div class="col-span-3 truncate uppercase" :class="getPriorityColor(item.priority)">{{ item.priority }}</div>
          <div class="col-span-4 truncate text-gray-300">{{ item.category }}</div>
          <div class="col-span-2 text-right" :class="item.confidence > 0.7 ? 'text-green-500' : item.confidence > 0.4 ? 'text-yellow-500' : 'text-red-500'">
            {{ Math.round(item.confidence * 100) }}%
          </div>
          <div class="col-span-1 text-center" :class="getSentimentColor(item.sentiment)">
            {{ getSentimentIndicator(item.sentiment) }}
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
