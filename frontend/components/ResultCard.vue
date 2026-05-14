<script setup lang="ts">
import { computed } from 'vue'
import { useToast } from '#imports'
import type { AnalysisResult } from '~/stores/enquiry'

const props = defineProps<{
  result: AnalysisResult
}>()

const toast = useToast()

const categoryColor = computed(() => {
  const cat = props.result.category?.toLowerCase()
  if (cat.includes('support')) return 'blue'
  if (cat.includes('complaint')) return 'red'
  if (cat.includes('new client')) return 'green'
  if (cat.includes('urgent')) return 'orange'
  return 'gray'
})

const priorityColor = computed(() => {
  const p = props.result.priority?.toLowerCase()
  if (p === 'urgent') return 'red'
  if (p === 'high') return 'orange'
  if (p === 'medium') return 'yellow'
  return 'green'
})

const confidencePercent = computed(() => {
  return Math.round(props.result.confidence * 100)
})

const confidenceColor = computed(() => {
  if (props.result.confidence > 0.7) return 'green'
  if (props.result.confidence >= 0.4) return 'yellow'
  return 'red'
})

const sentimentDisplay = computed(() => {
  const s = props.result.sentiment?.toLowerCase()
  if (s === 'positive') return { icon: 'i-heroicons-arrow-trending-up', label: 'POSITIVE', color: 'green' as const }
  if (s === 'negative') return { icon: 'i-heroicons-arrow-trending-down', label: 'NEGATIVE', color: 'red' as const }
  return { icon: 'i-heroicons-arrows-right-left', label: 'NEUTRAL', color: 'gray' as const }
})

async function copyToClipboard() {
  try {
    await navigator.clipboard.writeText(props.result.suggested_response)
    toast.add({
      title: 'Copied to clipboard',
      description: 'Suggested response copied successfully.',
      icon: 'i-heroicons-check-circle',
      color: 'green'
    })
  } catch {
    toast.add({
      title: 'Copy failed',
      description: 'Unable to copy text to clipboard.',
      icon: 'i-heroicons-x-circle',
      color: 'red'
    })
  }
}
</script>

<template>
  <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-0' } }">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-cpu-chip" class="w-5 h-5 text-primary-400" />
        <h2 class="text-sm font-mono font-semibold text-gray-200 uppercase tracking-wider">Analysis Payload</h2>
      </div>
      <div class="text-xs font-mono text-gray-500">
        <ClientOnly>
          ID: {{ Math.random().toString(36).substring(2, 10).toUpperCase() }}
        </ClientOnly>
      </div>
    </div>

    <div class="p-4 sm:p-6 space-y-6">
      
      <!-- Top Metrics Grid -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div class="bg-gray-900 border border-gray-800 rounded-md p-3">
          <div class="text-xs font-mono text-gray-500 mb-1">CATEGORY</div>
          <UBadge :color="categoryColor" variant="subtle" size="sm" class="font-mono">{{ result.category }}</UBadge>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-md p-3">
          <div class="text-xs font-mono text-gray-500 mb-1">PRIORITY</div>
          <UBadge :color="priorityColor" variant="subtle" size="sm" class="font-mono uppercase">{{ result.priority }}</UBadge>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-md p-3">
          <div class="text-xs font-mono text-gray-500 mb-1">SENTIMENT</div>
          <UBadge :color="sentimentDisplay.color" variant="subtle" size="sm" :icon="sentimentDisplay.icon" class="font-mono">
            {{ sentimentDisplay.label }}
          </UBadge>
        </div>
        <div class="bg-gray-900 border border-gray-800 rounded-md p-3">
          <div class="text-xs font-mono text-gray-500 mb-1">CONFIDENCE</div>
          <div class="flex items-center gap-2">
            <span class="text-lg font-bold font-mono" :class="`text-${confidenceColor}-400`">{{ confidencePercent }}%</span>
            <UMeter :value="confidencePercent" :color="confidenceColor" size="sm" />
          </div>
        </div>
      </div>

      <!-- Vague Warning -->
      <UAlert
        v-if="result.is_vague"
        icon="i-heroicons-exclamation-triangle"
        color="amber"
        variant="subtle"
        title="INSUFFICIENT DATA"
        description="The AI model detected low signal-to-noise ratio. Manual review recommended."
        :ui="{ title: 'font-mono text-sm uppercase', description: 'text-xs' }"
      />

      <!-- Two-column Layout for Output -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Suggested Response -->
        <div class="flex flex-col h-full">
          <div class="flex items-center justify-between mb-2">
            <h3 class="text-xs font-mono text-gray-400 uppercase tracking-wider">Suggested Response</h3>
            <UButton
              icon="i-heroicons-clipboard-document"
              size="2xs"
              color="gray"
              variant="ghost"
              @click="copyToClipboard"
            >
              COPY
            </UButton>
          </div>
          <div class="flex-1 bg-gray-900 border border-gray-800 rounded-md p-4 relative group font-mono text-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
            <span class="text-primary-500 select-none">> </span>{{ result.suggested_response }}
          </div>
        </div>

        <!-- Recommended Actions & Reasoning -->
        <div class="flex flex-col gap-4">
          <div v-if="result.recommended_actions?.length">
            <h3 class="text-xs font-mono text-gray-400 uppercase tracking-wider mb-2">Execution Protocol</h3>
            <div class="bg-gray-900 border border-gray-800 rounded-md p-3 space-y-2">
              <div v-for="(action, idx) in result.recommended_actions" :key="idx" class="flex gap-3 text-sm text-gray-300 font-mono">
                <span class="text-primary-500">[{{ idx + 1 }}]</span>
                <span>{{ action }}</span>
              </div>
            </div>
          </div>

          <div v-if="result.reasoning">
            <UAccordion
              :items="[{ label: 'MODEL_REASONING.log', content: result.reasoning }]"
              color="gray"
              variant="ghost"
              :ui="{ default: { class: 'bg-gray-900 border border-gray-800 rounded-md' }, item: { padding: 'px-4 pb-4 pt-0 text-xs font-mono text-gray-400' } }"
            >
              <template #default="{ item, open }">
                <UButton color="gray" variant="ghost" class="w-full text-xs font-mono text-left text-gray-400 hover:bg-gray-800/50" :ui="{ rounded: 'rounded-none', padding: { sm: 'p-3' } }">
                  <UIcon name="i-heroicons-chevron-right-20-solid" class="w-4 h-4 transition-transform duration-200" :class="[open && 'rotate-90']" />
                  <span class="truncate">{{ item.label }}</span>
                </UButton>
              </template>
              <template #item="{ item }">
                <p class="whitespace-pre-wrap">{{ item.content }}</p>
              </template>
            </UAccordion>
          </div>
        </div>
      </div>
      
    </div>
  </UCard>
</template>
