// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    '@nuxtjs/supabase'
  ],
  supabase: {
    redirectOptions: {
      login: '/auth/login',
      callback: '/auth/callback',
      exclude: ['/'],
    }
  },
  runtimeConfig: {
    public: {
      apiUrl: process.env.VITE_API_URL || 'http://localhost:5000'
    }
  },
  app: {
    head: {
      title: 'Murþrą - AI-Driven Murder Mystery',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { hid: 'description', name: 'description', content: 'A personalized, AI-driven detective experience that adapts to the player\'s psychology and decisions.' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})
