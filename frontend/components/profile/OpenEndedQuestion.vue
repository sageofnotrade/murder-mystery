<template>
  <div class="mb-8">
    <h3 class="text-lg font-semibold text-gray-200 mb-3">{{ question }}</h3>
    <textarea 
      :id="id" 
      v-model="responseText" 
      rows="4" 
      class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent text-gray-200"
      :placeholder="placeholder"
      :maxlength="maxLength"
    ></textarea>
    <div class="flex justify-between mt-1">
      <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      <p class="text-xs text-gray-400">{{ responseText.length }}/{{ maxLength }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  question: {
    type: String,
    required: true
  },
  value: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Share your thoughts...'
  },
  maxLength: {
    type: Number,
    default: 500
  },
  minLength: {
    type: Number,
    default: 0
  },
  required: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:value', 'validate']);

const responseText = ref(props.value);
const error = ref('');

watch(responseText, (newValue) => {
  emit('update:value', newValue);
  validateField();
});

const validateField = () => {
  if (props.required && !responseText.value.trim()) {
    error.value = 'This question requires an answer';
    emit('validate', false);
    return false;
  }
  
  if (props.minLength > 0 && responseText.value.trim().length < props.minLength) {
    error.value = `Response must be at least ${props.minLength} characters`;
    emit('validate', false);
    return false;
  }
  
  error.value = '';
  emit('validate', true);
  return true;
};

// Expose validate method to parent
defineExpose({
  validate: validateField
});
</script>
