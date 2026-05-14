export default defineNuxtConfig({
  compatibilityDate: '2025-05-11',
  devtools: { enabled: false },
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt'
  ],
  colorMode: {
    preference: 'dark' // Enforce dark mode for FinTech aesthetic
  },
  ui: {
    global: true,
  }
})
