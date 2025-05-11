<template>
  <button
    :class="[
      'px-4 py-2 rounded-lg font-semibold transition-colors',
      variant === 'primary' && 'bg-mystery-accent text-mystery-dark hover:bg-mystery-accent/90',
      variant === 'secondary' && 'border border-mystery-accent text-mystery-accent hover:bg-mystery-accent/10',
      variant === 'text' && 'text-mystery-accent hover:text-mystery-accent/80',
      disabled && 'opacity-50 cursor-not-allowed',
      className
    ]"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="inline-block animate-spin mr-2">⟳</span>
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'text'
  disabled?: boolean
  loading?: boolean
  className?: string
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  disabled: false,
  loading: false,
  className: ''
})

defineEmits<{
  (e: 'click'): void
}>()
</script> 