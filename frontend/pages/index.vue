<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useEnquiryStore } from '~/stores/enquiry'
import { useAuthStore } from '~/stores/auth'
import AdminLogin from '~/components/AdminLogin.vue'

const store = useEnquiryStore()
const authStore = useAuthStore()
const apiHealthy = ref<boolean | null>(null)

onMounted(async () => {
  store.fetchHistory()
  try {
    const config = useRuntimeConfig()
    const res = await $fetch<{ status: string }>(`${config.public.apiBase}/health`)
    apiHealthy.value = res?.status === 'healthy'
  } catch {
    apiHealthy.value = false
  }
})

// KPI Data
const totalEnquiries = computed(() => store.history.length)
const urgentEnquiries = computed(() => store.history.filter(h => h.priority?.toLowerCase() === 'urgent').length)
const avgConfidence = computed(() => {
  if (!store.history.length) return 0
  const sum = store.history.reduce((acc, curr) => acc + curr.confidence, 0)
  return Math.round((sum / store.history.length) * 100)
})

const currentTab = ref('Dashboard')

const navigation = computed(() => [
  { name: 'Dashboard', icon: 'i-heroicons-home', current: currentTab.value === 'Dashboard' },
  { name: 'Analytics', icon: 'i-heroicons-chart-bar', current: currentTab.value === 'Analytics' },
  { name: 'Alerts', icon: 'i-heroicons-bell', current: currentTab.value === 'Alerts', badge: urgentEnquiries.value },
  { name: 'Settings', icon: 'i-heroicons-cog-8-tooth', current: currentTab.value === 'Settings' },
])

// Analytics Computed Data
const categoryDistribution = computed(() => {
  const counts: Record<string, number> = {}
  store.history.forEach(h => {
    counts[h.category] = (counts[h.category] || 0) + 1
  })
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
})

const priorityDistribution = computed(() => {
  const counts: Record<string, number> = {}
  store.history.forEach(h => {
    counts[h.priority] = (counts[h.priority] || 0) + 1
  })
  return Object.entries(counts).map(([name, count]) => ({ name, count }))
})

// Alerts Computed Data
const urgentAlertsList = computed(() => {
  return store.history.filter(h => h.priority?.toLowerCase() === 'urgent')
})

// Settings Data
const newPassword = ref('')
const confirmPassword = ref('')
const passwordChangeSuccess = ref(false)
const passwordChangeError = ref('')

function handlePasswordChange() {
  passwordChangeSuccess.value = false
  passwordChangeError.value = ''
  
  if (newPassword.value !== confirmPassword.value) {
    passwordChangeError.value = 'Passwords do not match'
    return
  }
  
  if (authStore.changePassword(newPassword.value)) {
    passwordChangeSuccess.value = true
    newPassword.value = ''
    confirmPassword.value = ''
    setTimeout(() => {
      passwordChangeSuccess.value = false
    }, 3000)
  } else {
    passwordChangeError.value = 'Password must be at least 6 characters long'
  }
}

</script>

<template>
  <div v-if="!authStore.isAuthenticated">
    <AdminLogin />
  </div>
  <div v-else class="flex h-screen bg-gray-900 text-gray-100 overflow-hidden font-sans">
    <!-- Sidebar -->
    <aside class="w-16 md:w-64 flex-shrink-0 bg-gray-950 border-r border-gray-800 flex flex-col transition-all duration-300">
      <div class="h-16 flex items-center justify-center md:justify-start md:px-6 border-b border-gray-800">
        <UIcon name="i-heroicons-cpu-chip" class="w-8 h-8 text-primary-500" />
        <span class="ml-3 font-bold text-lg hidden md:block tracking-wider text-white">AlFRED<span class="text-primary-500">.AI</span></span>
      </div>
      <nav class="flex-1 overflow-y-auto py-4 space-y-1 px-2 md:px-4">
        <a v-for="item in navigation" :key="item.name" href="#"
          @click.prevent="currentTab = item.name"
          :class="[item.current ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800 hover:text-white', 'group flex items-center px-2 py-3 md:py-2 text-sm font-medium rounded-md']"
        >
          <UIcon :name="item.icon" :class="[item.current ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-300', 'flex-shrink-0 w-6 h-6 md:mr-3']" />
          <span class="hidden md:block flex-1">{{ item.name }}</span>
          <span v-if="item.badge && item.badge > 0" class="hidden md:inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium rounded-full bg-red-500 text-white">
            {{ item.badge }}
          </span>
        </a>
      </nav>
      <div class="p-4 border-t border-gray-800 flex justify-between md:justify-start items-center">
        <div class="flex items-center">
          <UAvatar src="https://avatars.githubusercontent.com/u/739984?v=4" alt="User" size="sm" />
          <div class="ml-3 hidden md:block">
            <p class="text-sm font-medium text-white">{{ authStore.user?.name || 'Lead Dev' }}</p>
            <p class="text-xs text-gray-500">{{ authStore.user?.role || 'System Admin' }}</p>
          </div>
        </div>
        <UButton 
          icon="i-heroicons-arrow-right-on-rectangle" 
          color="gray" 
          variant="ghost" 
          size="sm" 
          class="hidden md:flex ml-auto"
          @click="authStore.logout()"
        />
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <!-- Top Header -->
      <header class="h-16 bg-gray-950 border-b border-gray-800 flex items-center justify-between px-4 sm:px-6 lg:px-8">
        <div class="flex items-center gap-4">
          <h1 class="text-xl font-semibold text-white tracking-tight">Intelligence Terminal</h1>
        </div>
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono text-gray-400 uppercase tracking-wider">Engine Status</span>
            <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-900 border border-gray-800">
              <span class="relative flex h-2 w-2">
                <span v-if="apiHealthy === true" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2" :class="apiHealthy === true ? 'bg-primary-500' : apiHealthy === false ? 'bg-red-500' : 'bg-gray-500'"></span>
              </span>
              <span class="text-xs font-mono text-gray-300">
                {{ apiHealthy === true ? 'ONLINE' : apiHealthy === false ? 'OFFLINE' : 'CONNECTING' }}
              </span>
            </div>
          </div>
          <ClientOnly>
            <span class="text-xs font-mono text-gray-500 hidden sm:block">SYS.TIME: {{ new Date().toISOString().split('T')[1].split('.')[0] }} UTC</span>
          </ClientOnly>
        </div>
      </header>

      <!-- Dashboard Body -->
      <main class="flex-1 overflow-y-auto bg-gray-900 p-4 sm:p-6 lg:p-8">
        <div class="max-w-8xl mx-auto space-y-6">
          
          <template v-if="currentTab === 'Dashboard'">
            <!-- KPI Row -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-4 sm:p-5' } }">
                <div class="flex items-center">
                  <div class="flex-shrink-0 p-3 rounded-md bg-blue-500/10 border border-blue-500/20">
                    <UIcon name="i-heroicons-document-magnifying-glass" class="w-6 h-6 text-blue-400" />
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-400 truncate font-mono uppercase tracking-wider">Total Processed</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-bold text-white">{{ totalEnquiries }}</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </UCard>
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-4 sm:p-5' } }">
                <div class="flex items-center">
                  <div class="flex-shrink-0 p-3 rounded-md bg-red-500/10 border border-red-500/20">
                    <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6 text-red-400" />
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-400 truncate font-mono uppercase tracking-wider">Urgent Flags</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-bold text-white">{{ urgentEnquiries }}</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </UCard>
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800', shadow: 'shadow-none', body: { padding: 'p-4 sm:p-5' } }">
                <div class="flex items-center">
                  <div class="flex-shrink-0 p-3 rounded-md bg-primary-500/10 border border-primary-500/20">
                    <UIcon name="i-heroicons-chart-bar-square" class="w-6 h-6 text-primary-400" />
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-400 truncate font-mono uppercase tracking-wider">Model Confidence</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-bold text-white">{{ avgConfidence }}%</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </UCard>
            </div>

            <!-- Main Layout -->
            <div class="flex flex-col lg:flex-row gap-6">
              <!-- Left Column: Input and Results -->
              <div class="w-full lg:w-7/12 xl:w-2/3 flex flex-col gap-6">
                <EnquiryForm />
                <transition
                  enter-active-class="transition ease-out duration-300"
                  enter-from-class="opacity-0 translate-y-4"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition ease-in duration-200"
                  leave-from-class="opacity-100 translate-y-0"
                  leave-to-class="opacity-0 translate-y-4"
                >
                  <ResultCard v-if="store.result" :result="store.result" />
                </transition>
              </div>
              
              <!-- Right Column: History/Order Book -->
              <aside class="w-full lg:w-5/12 xl:w-1/3">
                <HistoryList />
              </aside>
            </div>
          </template>

          <template v-else-if="currentTab === 'Analytics'">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800' }">
                <template #header>
                  <h3 class="text-lg font-medium text-white font-mono">Category Distribution</h3>
                </template>
                <div class="space-y-4">
                  <div v-for="item in categoryDistribution" :key="item.name" class="flex items-center justify-between">
                    <span class="text-sm text-gray-400">{{ item.name }}</span>
                    <div class="flex items-center gap-3 w-1/2">
                      <div class="h-2 flex-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full bg-blue-500" :style="{ width: `${(item.count / totalEnquiries) * 100}%` }"></div>
                      </div>
                      <span class="text-sm font-bold text-white w-8 text-right">{{ item.count }}</span>
                    </div>
                  </div>
                  <div v-if="categoryDistribution.length === 0" class="text-sm text-gray-500 text-center py-4">No data available</div>
                </div>
              </UCard>
              
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800' }">
                <template #header>
                  <h3 class="text-lg font-medium text-white font-mono">Priority Distribution</h3>
                </template>
                <div class="space-y-4">
                  <div v-for="item in priorityDistribution" :key="item.name" class="flex items-center justify-between">
                    <span class="text-sm text-gray-400 capitalize">{{ item.name }}</span>
                    <div class="flex items-center gap-3 w-1/2">
                      <div class="h-2 flex-1 bg-gray-800 rounded-full overflow-hidden">
                        <div class="h-full bg-primary-500" :style="{ width: `${(item.count / totalEnquiries) * 100}%` }"></div>
                      </div>
                      <span class="text-sm font-bold text-white w-8 text-right">{{ item.count }}</span>
                    </div>
                  </div>
                  <div v-if="priorityDistribution.length === 0" class="text-sm text-gray-500 text-center py-4">No data available</div>
                </div>
              </UCard>
            </div>
          </template>

          <template v-else-if="currentTab === 'Alerts'">
            <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800' }">
              <template #header>
                <div class="flex items-center justify-between">
                  <h3 class="text-lg font-medium text-white font-mono flex items-center gap-2">
                    <UIcon name="i-heroicons-exclamation-triangle" class="text-red-500 w-5 h-5" />
                    Urgent Alerts
                  </h3>
                  <UBadge color="red" variant="subtle">{{ urgentAlertsList.length }} Active</UBadge>
                </div>
              </template>
              <div v-if="urgentAlertsList.length > 0" class="space-y-4">
                <div v-for="alert in urgentAlertsList" :key="alert.timestamp" class="p-4 border border-red-900/50 bg-red-950/20 rounded-lg">
                  <div class="flex justify-between items-start mb-2">
                    <span class="text-xs font-mono text-red-400">{{ alert.timestamp ? new Date(alert.timestamp).toLocaleString() : 'Unknown Date' }}</span>
                    <UBadge color="red" size="sm">URGENT</UBadge>
                  </div>
                  <p class="text-sm text-gray-300 mb-3">{{ alert.enquiry }}</p>
                  <div class="bg-gray-900 p-3 rounded text-sm border border-gray-800">
                    <strong class="text-gray-400 block mb-1">Recommended Action:</strong>
                    <ul class="list-disc pl-5 text-gray-300 space-y-1">
                      <li v-for="(action, i) in alert.recommended_actions" :key="i">{{ action }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div v-else class="flex flex-col items-center justify-center py-12">
                <UIcon name="i-heroicons-check-circle" class="w-12 h-12 text-green-500 mb-4" />
                <p class="text-gray-400 font-mono">No active system anomalies detected.</p>
              </div>
            </UCard>
          </template>

          <template v-else-if="currentTab === 'Settings'">
            <div class="max-w-2xl mx-auto">
              <UCard :ui="{ background: 'bg-gray-950', ring: 'ring-1 ring-gray-800' }">
                <template #header>
                  <h3 class="text-lg font-medium text-white font-mono flex items-center gap-2">
                    <UIcon name="i-heroicons-shield-check" class="text-primary-500 w-5 h-5" />
                    Security Settings
                  </h3>
                </template>
                <form @submit.prevent="handlePasswordChange" class="space-y-6">
                  <div>
                    <h4 class="text-sm font-medium text-gray-400 mb-4 uppercase tracking-wider font-mono">Change Admin Password</h4>
                    
                    <div class="space-y-4">
                      <UFormGroup label="New Password">
                        <UInput v-model="newPassword" type="password" icon="i-heroicons-key" placeholder="Enter new password" />
                      </UFormGroup>
                      
                      <UFormGroup label="Confirm Password">
                        <UInput v-model="confirmPassword" type="password" icon="i-heroicons-key" placeholder="Confirm new password" />
                      </UFormGroup>
                    </div>
                  </div>
                  
                  <div v-if="passwordChangeSuccess" class="p-3 bg-green-900/20 border border-green-900/50 rounded text-green-400 text-sm font-mono">
                    Password updated successfully!
                  </div>
                  
                  <div v-if="passwordChangeError" class="p-3 bg-red-900/20 border border-red-900/50 rounded text-red-400 text-sm font-mono">
                    {{ passwordChangeError }}
                  </div>
                  
                  <div class="pt-4 border-t border-gray-800 flex justify-end">
                    <UButton type="submit" color="primary" class="font-mono">UPDATE PASSWORD</UButton>
                  </div>
                </form>
              </UCard>
            </div>
          </template>

        </div>
      </main>
    </div>
  </div>
</template>

<style>
/* Custom Scrollbar for FinTech aesthetic */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: #111827;
}
::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #4B5563;
}
</style>
