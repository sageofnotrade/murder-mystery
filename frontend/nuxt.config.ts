import { defineNuxtConfig } from 'nuxt/config'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  plugins: [
    '~/plugins/lucide.client.ts',
    '~/plugins/persistedstate.client.ts'
  ],
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  
  ],
  typescript: {
    strict: true,
    typeCheck: true,
    tsConfig: {
      compilerOptions: {
        module: 'ESNext',
        moduleResolution: 'Bundler',
        target: 'ESNext'
      }
    }
  },
  alias: {
    '@': '/<rootDir>',
  },
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.NUXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api',
      apiUrl: process.env.VITE_API_URL || 'http://localhost:5000',
      supabaseUrl: process.env.SUPABASE_URL,
      supabaseKey: process.env.SUPABASE_KEY,
      supabaseRedirectOptions: {
        login: '/auth/login',
        register: '/auth/register',
        callback: '/auth/callback',
        exclude: ['/', '/auth/register', '/auth/login']
      }
    }
  },
  app: {
    head: {
      title: 'Murþrą - AI-Driven Murder Mystery',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'A personalized, AI-driven detective experience that adapts to the player\'s psychology and decisions.'
        }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  }
})
