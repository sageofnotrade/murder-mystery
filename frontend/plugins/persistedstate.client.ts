import { defineNuxtPlugin } from '#app'
// @ts-expect-error: missing types from pinia-plugin-persistedstate
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

export default defineNuxtPlugin((nuxtApp) => {
  (nuxtApp.$pinia as any).use(piniaPluginPersistedstate)
})