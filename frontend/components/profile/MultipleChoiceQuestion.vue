<template>
  <div class="mb-8">
    <h3 class="text-lg font-semibold text-gray-200 mb-3">{{ question }}</h3>
    <div class="space-y-3">
      <div 
        v-for="(option, index) in options" 
        :key="index" 
        class="flex items-center"
      >
        <input 
          type="radio" 
          :id="`${id}-option-${index}`" 
          :name="id" 
          :value="option" 
          v-model="selectedOption" 
          class="mr-3 text-mystery-accent focus:ring-mystery-accent focus:ring-offset-mystery-dark" 
        />
        <label 
          :for="`${id}-option-${index}`" 
          class="text-gray-300 cursor-pointer hover:text-gray-100"
        >
          {{ option }}
        </label>
      </div>
    </div>
    <p v-if="error" class="mt-2 text-sm text-red-500">{{ error }}</p>
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
  options: {
    type: Array,
    required: true
  },
  value: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:value', 'validate']);

const selectedOption = ref(props.value);
const error = ref('');

watch(selectedOption, (newValue) => {
  emit('update:value', newValue);
  validateField();
});

const validateField = () => {
  if (props.required && !selectedOption.value) {
    error.value = 'This question requires an answer';
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
