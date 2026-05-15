export default defineNuxtConfig({
  compatibilityDate: '2025-05-11',
  devtools: { enabled: false },
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5000/api'
    }
  },
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@nuxtjs/supabase'
  ],
  supabase: {
    redirect: false // Disable default redirect to login page for this demo
  },
  colorMode: {
    preference: 'dark' // Enforce dark mode for FinTech aesthetic
  },
  ui: {
    global: true,
  }
})
