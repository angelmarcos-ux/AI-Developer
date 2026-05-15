<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const password = ref('')
const error = ref('')

const showHint = computed(() => auth.currentPassword === 'admin123')

function handleLogin() {
  if (auth.login(password.value)) {
    error.value = ''
  } else {
    error.value = showHint.value ? 'Invalid authorization key. Try "admin123".' : 'Invalid authorization key. Password has been changed.'
  }
}
</script>

<template>
  <div class="flex items-center justify-center h-screen w-screen bg-gray-950 text-gray-100 font-sans">
    <UCard class="w-full max-w-sm" :ui="{ background: 'bg-gray-900', ring: 'ring-1 ring-gray-800' }">
      <div class="text-center mb-6">
        <UIcon name="i-heroicons-cpu-chip" class="w-12 h-12 text-primary-500 mx-auto" />
        <h1 class="mt-4 text-2xl font-bold tracking-wider text-white">AlFRED<span class="text-primary-500">.AI</span></h1>
        <p class="text-sm text-gray-400 mt-2 font-mono uppercase">Secure Access Terminal</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <UInput
            v-model="password"
            type="password"
            icon="i-heroicons-key"
            placeholder="Enter authorization key..."
            :ui="{ 
              icon: { base: 'text-gray-500' }
            }"
            autofocus
            class="w-full"
          />
        </div>
        <p v-if="showHint" class="text-gray-500 text-xs font-mono text-center">Hint: admin123</p>
        <p v-if="error" class="text-red-500 text-xs font-mono text-center">{{ error }}</p>
        <UButton
          type="submit"
          color="primary"
          block
          class="font-mono tracking-widest mt-2"
        >
          AUTHENTICATE
        </UButton>
      </form>
    </UCard>
  </div>
</template>
