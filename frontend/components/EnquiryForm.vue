<script setup lang="ts">
import { ref, computed } from 'vue'
import { useEnquiryStore } from '~/stores/enquiry'

const store = useEnquiryStore()

const enquiryText = ref('')
const validationError = ref('')
const maxChars = 5000

const isOverLimit = computed(() => enquiryText.value.length > maxChars)
const charCountClass = computed(() => {
  if (isOverLimit.value) return 'text-red-500'
  if (enquiryText.value.length > maxChars * 0.9) return 'text-amber-500'
  return 'text-gray-500'
})

async function handleSubmit() {
  validationError.value = ''

  if (!enquiryText.value.trim()) {
    validationError.value = 'ERR: EMPTY_PAYLOAD - Input stream cannot be empty.'
    return
  }
  if (isOverLimit.value) {
    validationError.value = 'ERR: OVERFLOW - Input stream exceeds maximum allowed bytes.'
    return
  }

  await store.submitEnquiry(enquiryText.value.trim())
}
</script>

<template>
  <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-0' } }">
    <!-- Header -->
    <div class="px-4 py-3 border-b border-gray-800 flex items-center justify-between bg-gray-900/50">
      <div class="flex items-center gap-2">
        <UIcon name="i-heroicons-command-line" class="w-5 h-5 text-primary-400" />
        <h2 class="text-sm font-mono font-semibold text-gray-200 uppercase tracking-wider">Command / Enquiry Input</h2>
      </div>
      <div class="flex items-center gap-2">
        <span class="flex h-2 w-2 rounded-full bg-green-500"></span>
        <span class="flex h-2 w-2 rounded-full bg-amber-500"></span>
        <span class="flex h-2 w-2 rounded-full bg-red-500"></span>
      </div>
    </div>

    <!-- Body -->
    <div class="p-4 space-y-4">
      <div class="relative rounded-md shadow-sm">
        <div class="absolute inset-y-0 left-0 pl-3 pt-3 pointer-events-none flex items-start">
          <span class="text-primary-500 font-mono text-sm">></span>
        </div>
        <textarea
          v-model="enquiryText"
          rows="6"
          :maxlength="maxChars + 100"
          class="block w-full rounded-md border-0 py-3 pl-8 pr-3 bg-gray-900 text-gray-300 ring-1 ring-inset ring-gray-800 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm sm:leading-6 font-mono resize-none placeholder:text-gray-700"
          placeholder="Enter natural language input for model classification..."
          :disabled="store.loading"
          @input="validationError = ''"
          @keydown.ctrl.enter="handleSubmit"
          @keydown.meta.enter="handleSubmit"
        ></textarea>
      </div>

      <div class="flex items-center justify-between">
        <div class="flex flex-col">
          <span v-if="validationError || store.error" class="text-xs font-mono text-red-500">
            {{ validationError || store.error }}
          </span>
          <span v-else class="text-xs font-mono text-gray-500">
            Press Ctrl+Enter to execute
          </span>
        </div>
        
        <div class="flex items-center gap-4">
          <span class="text-xs font-mono" :class="charCountClass">
            BYTES: {{ enquiryText.length }}/{{ maxChars }}
          </span>
          <div class="flex items-center gap-2">
            <UButton
              color="gray"
              variant="solid"
              :disabled="store.loading || !enquiryText.trim()"
              @click="enquiryText = ''; validationError = ''; store.error = null;"
              icon="i-heroicons-trash"
              class="font-mono text-xs uppercase tracking-wider"
            >
              CLEAR
            </UButton>
            <UButton
              color="primary"
              variant="solid"
              :loading="store.loading"
              :disabled="store.loading || !enquiryText.trim() || isOverLimit"
              @click="handleSubmit"
              icon="i-heroicons-bolt"
              class="font-mono text-xs uppercase tracking-wider"
            >
              {{ store.loading ? 'Processing...' : 'Execute' }}
            </UButton>
          </div>
        </div>
      </div>
    </div>
  </UCard>
</template>
