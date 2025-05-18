<template>
  <div class="mb-8">
    <h3 class="text-lg font-semibold text-gray-200 mb-3">{{ question }}</h3>
    <div class="mt-4">
      <div class="flex justify-between text-sm text-gray-400 mb-2">
        <span>{{ minLabel }}</span>
        <span>{{ maxLabel }}</span>
      </div>
      <input 
        type="range" 
        :id="id" 
        :min="min" 
        :max="max" 
        :step="step" 
        v-model.number="sliderValue" 
        class="w-full accent-mystery-accent bg-mystery-dark h-2 rounded-lg appearance-none cursor-pointer" 
      />
      <div class="text-center mt-2 text-gray-300">
        Selected value: {{ sliderValue }}
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
  min: {
    type: Number,
    default: 1
  },
  max: {
    type: Number,
    default: 5
  },
  step: {
    type: Number,
    default: 1
  },
  value: {
    type: Number,
    default: null
  },
  minLabel: {
    type: String,
    default: 'Strongly Disagree'
  },
  maxLabel: {
    type: String,
    default: 'Strongly Agree'
  },
  required: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:value', 'validate']);

// Default to middle value if no value provided
const sliderValue = ref(props.value !== null ? props.value : Math.floor((props.max + props.min) / 2));
const error = ref('');

watch(sliderValue, (newValue) => {
  emit('update:value', newValue);
  validateField();
});

const validateField = () => {
  if (props.required && sliderValue.value === null) {
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

<style scoped>
/* Custom styling for the slider track in different browsers */
input[type="range"]::-webkit-slider-runnable-track {
  background: linear-gradient(to right, #1F2937, #6366F1);
  height: 0.5rem;
  border-radius: 0.25rem;
}

input[type="range"]::-moz-range-track {
  background: linear-gradient(to right, #1F2937, #6366F1);
  height: 0.5rem;
  border-radius: 0.25rem;
}

/* Custom styling for the slider thumb in different browsers */
input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 1.25rem;
  height: 1.25rem;
  background: #6366F1;
  border-radius: 50%;
  cursor: pointer;
  margin-top: -0.375rem; /* to center the thumb on the track */
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}

input[type="range"]::-moz-range-thumb {
  width: 1.25rem;
  height: 1.25rem;
  background: #6366F1;
  border-radius: 50%;
  cursor: pointer;
  border: none;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.5);
}
</style>
