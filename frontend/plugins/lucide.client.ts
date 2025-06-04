import { defineNuxtPlugin } from '#app'
import { ArrowLeft, RefreshCcw } from 'lucide-vue-next'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.component('ArrowLeftIcon', ArrowLeft)
  nuxtApp.vueApp.component('RefreshIcon', RefreshCcw)
})
