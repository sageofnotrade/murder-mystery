import { defineNuxtPlugin, useRuntimeConfig } from '#app'
import { createClient } from '@supabase/supabase-js'


const supabaseUrl = useRuntimeConfig().public.supabaseUrl as string
const supabaseKey = useRuntimeConfig().public.supabaseKey as string

export default defineNuxtPlugin(() => {
  const supabase = createClient(supabaseUrl, supabaseKey)

  return {
    provide: {
      supabase
    }
  }
})
