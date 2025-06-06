<template>
  <div class="bg-mystery-medium p-6 rounded-lg shadow-lg">
    <div class="mb-8">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-2xl font-bold text-mystery-accent">{{ currentSection.title }}</h2>
        <div class="text-sm text-gray-400">
          Section {{ currentSectionIndex + 1 }} of {{ questionnaire.sections.length }}
        </div>
      </div>
      <p class="text-gray-300 mb-6">{{ currentSection.description }}</p>
      
      <!-- Progress Bar -->
      <div class="w-full bg-mystery-dark rounded-full h-2 mb-8">
        <div 
          class="bg-mystery-accent h-2 rounded-full transition-all duration-300"
          :style="{ width: `${progressPercentage}%` }"
        ></div>
      </div>
    </div>
    
    <!-- Questions -->
    <div>
      <component 
        v-for="(question, index) in currentSection.questions"
        :key="question.id"
        :is="getComponentType(question.type)"
        :id="question.id"
        :question="question.question"
        v-bind="getQuestionProps(question)"
        :value="responses[question.id]"
        @update:value="(val) => updateResponse(question.id, val)"
        @validate="(valid) => updateValidity(question.id, valid)"
        :required="true"
        ref="questionRefs"
      ></component>
    </div>

    <!-- Navigation Buttons -->
    <div class="flex justify-between mt-8">
      <button 
        v-if="currentSectionIndex > 0"
        @click="previousSection"
        class="px-4 py-2 border border-mystery-accent text-mystery-accent rounded-lg hover:bg-mystery-accent/10 transition-colors"
      >
        Previous
      </button>
      <div v-else></div>
      
      <button 
        v-if="currentSectionIndex < questionnaire.sections.length - 1"
        @click="nextSection"
        class="px-4 py-2 bg-mystery-accent text-mystery-dark rounded-lg hover:bg-mystery-accent/90 transition-colors"
        :disabled="!isSectionValid"
      >
        Next
      </button>
      <button 
        v-else
        @click="submitQuestionnaire"
        class="px-4 py-2 bg-mystery-accent text-mystery-dark rounded-lg hover:bg-mystery-accent/90 transition-colors"
        :disabled="!isSectionValid || submitting"
      >
        {{ submitting ? 'Submitting...' : 'Submit' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue';
import { useProfileQuestionnaireStore } from '~/stores/profileQuestionnaire';
import MultipleChoiceQuestion from './MultipleChoiceQuestion.vue';
import SliderQuestion from './SliderQuestion.vue';
import OpenEndedQuestion from './OpenEndedQuestion.vue';

interface Question {
  id: string | number
  type: string
  question: string
  options?: any[]
  min?: number
  max?: number
  minLabel?: string
  maxLabel?: string
  placeholder?: string
  maxLength?: number
}

type Responses = Record<string | number, any>
type ValidFields = Record<string | number, boolean>

const props = defineProps({
  questionnaire: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['submit', 'complete']);

const store = useProfileQuestionnaireStore();
const currentSectionIndex = ref<number>(0)
const responses = ref<Responses>({})
const validFields = ref<ValidFields>({})
const questionRefs = ref<(any | null)[]>([])
const submitting = ref(false)

// Load saved responses if available
onMounted(() => {
  if (store.responses) {
    responses.value = store.responses;
  }
  
  if (store.currentSectionIndex !== null) {
    currentSectionIndex.value = store.currentSectionIndex;
  }
  
  // Validate initial fields after component is mounted
  nextTick(() => {
    if (questionRefs.value.length > 0) {
      questionRefs.value.forEach(ref => {
        if (ref && typeof ref.validate === 'function') {
          ref.validate();
        }
      });
    }
  });
});

const currentSection = computed(() => {
  return props.questionnaire.sections[currentSectionIndex.value];
});

const progressPercentage = computed(() => {
  const totalSections = props.questionnaire.sections.length;
  const sectionsCompleted = currentSectionIndex.value;

  let baseProgress = (sectionsCompleted / totalSections) * 100;

  const totalQuestionsInSection = currentSection.value.questions.length;
  let completedQuestionsInSection = 0;

  currentSection.value.questions.forEach((question: Question) => {
    if (responses.value[question.id]) {
      completedQuestionsInSection++;
    }
  });

  const additionalProgress = (completedQuestionsInSection / totalQuestionsInSection) * (1 / totalSections) * 100;

  return Math.min(Math.round(baseProgress + additionalProgress), 100);
});

const isSectionValid = computed(() => {
  // Check if all required questions in the current section have valid answers
  return currentSection.value.questions.every((question: { id: string }) => validFields.value[question.id]);

});

const getComponentType = (type: string) => {
  switch (type) {
    case 'multiple-choice':
      return MultipleChoiceQuestion;
    case 'slider':
      return SliderQuestion;
    case 'open-ended':
      return OpenEndedQuestion;
    default:
      return MultipleChoiceQuestion;
  }
};

const getQuestionProps = (question: Question) => {
  switch (question.type) {
    case 'multiple-choice':
      return { options: question.options };
    case 'slider':
      return { 
        min: question.min || 1, 
        max: question.max || 5, 
        minLabel: question.minLabel || 'Strongly Disagree', 
        maxLabel: question.maxLabel || 'Strongly Agree' 
      };
    case 'open-ended':
      return { 
        placeholder: question.placeholder || 'Share your thoughts...',
        maxLength: question.maxLength || 500
      };
    default:
      return {};
  }
};

const updateResponse = (questionId: string | number, value: any) => {
  responses.value[questionId] = value;
  store.updateResponses(responses.value);
};

const updateValidity = (questionId: string | number, isValid: boolean) => {
  validFields.value[questionId] = isValid;
};

const nextSection = () => {
  if (currentSectionIndex.value < props.questionnaire.sections.length - 1) {
    currentSectionIndex.value++;
    store.updateCurrentSectionIndex(currentSectionIndex.value);
    
    // Validate fields in the new section after component updates
    nextTick(() => {
      if (questionRefs.value.length > 0) {
        questionRefs.value.forEach(ref => {
          if (ref && typeof ref.validate === 'function') {
            ref.validate();
          }
        });
      }
    });
  }
};

const previousSection = () => {
  if (currentSectionIndex.value > 0) {
    currentSectionIndex.value--;
    store.updateCurrentSectionIndex(currentSectionIndex.value);
  }
};

const submitQuestionnaire = async () => {
  try {
    submitting.value = true;
    
    // Use the store's submit action
    await store.submitResponses();
    
    // Emit events for parent components
    emit('submit', responses.value);
    emit('complete');
    
    // Reset store after submission
    store.resetQuestionnaire();
  } catch (error) {
    console.error('Error submitting questionnaire:', error);
  } finally {
    submitting.value = false;
  }
};
</script>
