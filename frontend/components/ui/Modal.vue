<template>
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
        @after-enter="onAfterEnter"
        @after-leave="onAfterLeave"
      >
        <div
          v-if="modelValue"
          class="fixed inset-0 z-50 overflow-y-auto"
          role="dialog"
          aria-modal="true"
          :aria-labelledby="titleId"
          :aria-describedby="descriptionId"
        >
          <!-- Backdrop -->
          <div
            class="fixed inset-0 bg-black transition-opacity"
            :class="[
              backdrop === 'blur' ? 'bg-opacity-50 backdrop-blur-sm' : 'bg-opacity-75',
              backdropClass
            ]"
            @click="handleBackdropClick"
          />
  
          <!-- Modal Container -->
          <div class="flex min-h-full items-center justify-center p-4">
            <div
              ref="modalRef"
              class="relative w-full transform overflow-hidden rounded-lg bg-mystery-dark shadow-xl transition-all"
              :class="[
                sizeClasses[size],
                variant === 'fullscreen' ? 'h-screen max-h-screen' : '',
                modalClass
              ]"
              @click.stop
              v-bind="$attrs"
            >
              <!-- Loading Overlay -->
              <Transition
                enter-active-class="transition-opacity duration-200"
                enter-from-class="opacity-0"
                enter-to-class="opacity-100"
                leave-active-class="transition-opacity duration-150"
                leave-from-class="opacity-100"
                leave-to-class="opacity-0"
              >
                <div
                  v-if="loading"
                  class="absolute inset-0 z-10 flex items-center justify-center bg-mystery-dark bg-opacity-75"
                >
                  <div class="flex flex-col items-center space-y-3">
                    <div class="h-12 w-12 animate-spin rounded-full border-4 border-mystery-accent border-t-transparent" />
                    <p v-if="loadingText" class="text-sm text-gray-400">{{ loadingText }}</p>
                  </div>
                </div>
              </Transition>
  
              <!-- Header -->
              <div
                v-if="!hideHeader"
                class="flex items-center justify-between border-b border-mystery-medium px-6 py-4"
                :class="headerClass"
              >
                <div class="flex items-center space-x-3">
                  <component
                    v-if="icon"
                    :is="icon"
                    class="h-5 w-5"
                    :class="iconColorClass"
                  />
                  <h3
                    :id="titleId"
                    class="text-lg font-semibold text-white"
                  >
                    {{ title }}
                  </h3>
                </div>
                <div class="flex items-center space-x-2">
                  <slot name="header-actions" />
                  <button
                    v-if="showClose"
                    @click="close"
                    class="rounded-full p-1.5 text-gray-400 transition-colors hover:bg-mystery-medium hover:text-white focus:outline-none focus:ring-2 focus:ring-mystery-accent"
                    :aria-label="closeAriaLabel"
                  >
                    <XIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>
  
              <!-- Content -->
              <div
                :id="descriptionId"
                class="overflow-y-auto"
                :class="[
                  contentPadding ? 'px-6 py-4' : '',
                  maxHeightClass,
                  contentClass
                ]"
                :style="contentStyle"
              >
                <slot />
              </div>
  
              <!-- Footer -->
              <div
                v-if="$slots.footer || showDefaultFooter"
                class="flex items-center border-t border-mystery-medium px-6 py-4"
                :class="[
                  footerAlign === 'left' ? 'justify-start' : 
                  footerAlign === 'center' ? 'justify-center' : 
                  'justify-end',
                  footerClass
                ]"
              >
                <slot name="footer">
                  <div v-if="showDefaultFooter" class="flex items-center gap-3">
                    <button
                      v-if="showCancel"
                      @click="handleCancel"
                      class="btn-secondary"
                      :disabled="loading"
                    >
                      {{ cancelText }}
                    </button>
                    <button
                      v-if="showConfirm"
                      @click="handleConfirm"
                      class="btn-primary"
                      :class="confirmButtonClass"
                      :disabled="loading || confirmDisabled"
                    >
                      <component
                        v-if="confirmIcon"
                        :is="confirmIcon"
                        class="mr-2 h-4 w-4"
                      />
                      {{ confirmText }}
                    </button>
                  </div>
                </slot>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </template>
  
  <script setup>
  import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
  import { XIcon } from '@heroicons/vue/outline'
  import { useFocusTrap } from '@vueuse/integrations/useFocusTrap'
  import { onKeyStroke } from '@vueuse/core'
  
  const props = defineProps({
    modelValue: {
      type: Boolean,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value)
    },
    variant: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'fullscreen', 'drawer'].includes(value)
    },
    showClose: {
      type: Boolean,
      default: true
    },
    closeOnBackdrop: {
      type: Boolean,
      default: true
    },
    closeOnEscape: {
      type: Boolean,
      default: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    loadingText: {
      type: String,
      default: ''
    },
    backdrop: {
      type: String,
      default: 'blur',
      validator: (value) => ['blur', 'dark'].includes(value)
    },
    icon: {
      type: [Object, Function],
      default: null
    },
    iconColor: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'primary', 'success', 'warning', 'danger'].includes(value)
    },
    hideHeader: {
      type: Boolean,
      default: false
    },
    contentPadding: {
      type: Boolean,
      default: true
    },
    maxHeight: {
      type: String,
      default: 'auto'
    },
    // Default footer props
    showDefaultFooter: {
      type: Boolean,
      default: false
    },
    showCancel: {
      type: Boolean,
      default: true
    },
    showConfirm: {
      type: Boolean,
      default: true
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    confirmIcon: {
      type: [Object, Function],
      default: null
    },
    confirmDisabled: {
      type: Boolean,
      default: false
    },
    confirmButtonClass: {
      type: String,
      default: ''
    },
    footerAlign: {
      type: String,
      default: 'right',
      validator: (value) => ['left', 'center', 'right'].includes(value)
    },
    // Custom classes
    modalClass: {
      type: String,
      default: ''
    },
    headerClass: {
      type: String,
      default: ''
    },
    contentClass: {
      type: String,
      default: ''
    },
    footerClass: {
      type: String,
      default: ''
    },
    backdropClass: {
      type: String,
      default: ''
    },
    // Accessibility
    closeAriaLabel: {
      type: String,
      default: 'Close modal'
    },
    role: {
      type: String,
      default: 'dialog'
    }
  })
  
  const emit = defineEmits([
    'update:modelValue',
    'close',
    'confirm',
    'cancel',
    'backdrop-click',
    'after-enter',
    'after-leave'
  ])
  
  // Refs
  const modalRef = ref(null)
  const titleId = computed(() => `modal-title-${Math.random().toString(36).substr(2, 9)}`)
  const descriptionId = computed(() => `modal-desc-${Math.random().toString(36).substr(2, 9)}`)
  
  // Size classes mapping
  const sizeClasses = {
    xs: 'max-w-xs',
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    '2xl': 'max-w-6xl',
    full: 'max-w-full mx-4'
  }
  
  // Icon color classes
  const iconColorClass = computed(() => {
    const colors = {
      default: 'text-gray-400',
      primary: 'text-mystery-accent',
      success: 'text-green-500',
      warning: 'text-yellow-500',
      danger: 'text-red-500'
    }
    return colors[props.iconColor] || colors.default
  })
  
  // Max height handling
  const maxHeightClass = computed(() => {
    if (props.variant === 'fullscreen') return 'h-full'
    if (props.maxHeight === 'auto') return ''
    return ''
  })
  
  const contentStyle = computed(() => {
    if (props.maxHeight !== 'auto' && props.variant !== 'fullscreen') {
      return { maxHeight: props.maxHeight }
    }
    return {}
  })
  
  // Focus trap
  const { activate: activateFocusTrap, deactivate: deactivateFocusTrap } = useFocusTrap(modalRef, {
    immediate: false,
    escapeDeactivates: false,
    allowOutsideClick: true
  })
  
  // Event handlers
  const close = () => {
    emit('update:modelValue', false)
    emit('close')
  }
  
  const handleBackdropClick = () => {
    emit('backdrop-click')
    if (props.closeOnBackdrop && !props.loading) {
      close()
    }
  }
  
  const handleConfirm = () => {
    emit('confirm')
  }
  
  const handleCancel = () => {
    emit('cancel')
    close()
  }
  
  const onAfterEnter = () => {
    nextTick(() => {
      activateFocusTrap()
      emit('after-enter')
    })
  }
  
  const onAfterLeave = () => {
    deactivateFocusTrap()
    emit('after-leave')
  }
  
  // Keyboard handling
  onKeyStroke('Escape', (e) => {
    if (props.modelValue && props.closeOnEscape && !props.loading) {
      e.preventDefault()
      close()
    }
  })
  
  // Prevent body scroll when modal is open
  watch(() => props.modelValue, (isOpen) => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  })
  
  onUnmounted(() => {
    document.body.style.overflow = ''
    deactivateFocusTrap()
  })
  </script>
  
  <style scoped>
  /* Button styles */
  .btn-primary {
    @apply inline-flex items-center justify-center rounded-md bg-mystery-accent px-4 py-2 text-sm font-medium text-white shadow-lg shadow-mystery-accent/25 transition-all hover:bg-mystery-accent/90 hover:shadow-xl hover:shadow-mystery-accent/30 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50 disabled:shadow-none;
  }
  
  .btn-secondary {
    @apply inline-flex items-center justify-center rounded-md border border-mystery-light bg-mystery-medium px-4 py-2 text-sm font-medium text-gray-300 transition-all hover:border-mystery-accent/50 hover:bg-mystery-light hover:text-white hover:shadow-lg hover:shadow-mystery-accent/10 focus:outline-none focus:ring-2 focus:ring-mystery-accent focus:ring-offset-2 focus:ring-offset-mystery-dark disabled:cursor-not-allowed disabled:opacity-50;
  }
  
  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.3);
  }
  
  ::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 4px;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.5);
  }
  </style>