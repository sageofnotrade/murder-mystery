<template>
  <div class="min-h-screen bg-mystery-dark py-8 px-4 md:px-8">
    <div class="max-w-4xl mx-auto">
      <div v-if="submitted" class="bg-mystery-medium p-8 rounded-lg shadow-lg text-center">
        <div class="text-5xl mb-6 text-green-500">✓</div>
        <h2 class="text-2xl font-bold text-mystery-accent mb-4">Profile Completed!</h2>
        <p class="text-gray-300 mb-6">
          Thank you for completing your psychological profile. We'll use this information to tailor your mystery experience.
        </p>
        <button 
          @click="navigateToDashboard"
          class="px-6 py-3 bg-mystery-accent text-mystery-dark rounded-lg hover:bg-mystery-accent/90 transition-colors"
        >
          Continue to Dashboard
        </button>
      </div>
      
      <div v-else>
        <h1 class="text-3xl md:text-4xl font-bold text-mystery-accent mb-3">Psychological Profile</h1>
        <p class="text-gray-300 mb-8">
          Complete this questionnaire to help us tailor your murder mystery experience to your psychological traits and preferences.
          Your answers will influence the types of mysteries, characters, and challenges you encounter.
        </p>
        
        <div v-if="loading" class="flex justify-center my-12">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-mystery-accent"></div>
        </div>
        
        <div v-else-if="error" class="bg-red-900/30 border border-red-800 p-6 rounded-lg mb-8">
          <h3 class="text-red-500 font-semibold mb-2">Error Loading Questionnaire</h3>
          <p class="text-gray-300">{{ error }}</p>
          <button 
            @click="loadQuestionnaire" 
            class="mt-4 px-4 py-2 bg-mystery-accent text-mystery-dark rounded-lg hover:bg-mystery-accent/90 transition-colors"
          >
            Try Again
          </button>
        </div>
        
        <PsychologicalQuestionnaire 
          v-else 
          :questionnaire="questionnaire" 
          @complete="handleCompletion"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useProfileQuestionnaireStore } from '~/stores/profileQuestionnaire';
import PsychologicalQuestionnaire from '~/components/profile/PsychologicalQuestionnaire.vue';

const loading = ref(true);
const error = ref(null);
const submitted = ref(false);
const questionnaire = ref(null);
const store = useProfileQuestionnaireStore();

onMounted(() => {
  loadQuestionnaire();
});

const loadQuestionnaire = async () => {
  try {
    loading.value = true;
    error.value = null;
    
    // In a real implementation, you would fetch this from an API
    // For now, we'll use a static structure
    questionnaire.value = {
      sections: [
        {
          title: "Problem-Solving Style",
          description: "How do you approach challenges?",
          questions: [
            {
              id: "problem_solving_1",
              type: "multiple-choice",
              question: "When faced with a complex problem, you prefer to:",
              options: [
                "Break it down into smaller parts",
                "Look for patterns and connections",
                "Trust your intuition",
                "Consult others for their perspective"
              ]
            },
            {
              id: "problem_solving_2",
              type: "multiple-choice",
              question: "When you're stuck on a problem, your first instinct is to:",
              options: [
                "Research similar problems and their solutions",
                "Take a break and return with fresh eyes",
                "Discuss it with someone else",
                "Try a completely different approach"
              ]
            },
            {
              id: "problem_solving_3",
              type: "slider",
              question: "I prefer to plan everything in detail rather than adapt as I go.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "Moral Compass",
          description: "How do you make ethical decisions?",
          questions: [
            {
              id: "moral_1",
              type: "slider",
              question: "Justice should always be served, even if it causes harm to innocent people.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "moral_2",
              type: "multiple-choice",
              question: "When someone commits a crime, which is more important?",
              options: [
                "Understanding why they did it",
                "Making sure they face consequences",
                "Rehabilitating them to prevent future crimes",
                "Protecting society from them"
              ]
            },
            {
              id: "moral_3",
              type: "open-ended",
              question: "Describe a situation where breaking the rules might be justified.",
              placeholder: "Share your perspective...",
              maxLength: 300
            }
          ]
        },
        {
          title: "Risk Tolerance",
          description: "How do you approach uncertain situations?",
          questions: [
            {
              id: "risk_1",
              type: "slider",
              question: "I enjoy situations with an element of danger or risk.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "risk_2",
              type: "multiple-choice",
              question: "When making an important decision, you prioritize:",
              options: [
                "Avoiding potential negative outcomes",
                "Maximizing potential benefits",
                "Finding a balanced approach",
                "Following established procedures"
              ]
            },
            {
              id: "risk_3",
              type: "slider",
              question: "I prefer familiar environments over new and unpredictable ones.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "Social Interaction",
          description: "How do you engage with others?",
          questions: [
            {
              id: "social_1",
              type: "multiple-choice",
              question: "In group settings, you typically:",
              options: [
                "Take charge and lead discussions",
                "Listen carefully and speak when necessary",
                "Observe people's behaviors and interactions",
                "Connect individually with specific people"
              ]
            },
            {
              id: "social_2",
              type: "slider",
              question: "I find it easy to tell when someone is hiding something.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "social_3",
              type: "open-ended",
              question: "How do you typically respond when you catch someone in a lie?",
              placeholder: "Describe your typical reaction...",
              maxLength: 300
            }
          ]
        },
        {
          title: "Mystery Preferences",
          description: "What elements do you enjoy in mystery stories?",
          questions: [
            {
              id: "mystery_1",
              type: "multiple-choice",
              question: "Which aspect of mystery stories do you find most compelling?",
              options: [
                "Complex puzzles to solve",
                "Psychological depth of characters",
                "Suspenseful atmosphere and tension",
                "Moral dilemmas and ethical questions"
              ]
            },
            {
              id: "mystery_2",
              type: "multiple-choice",
              question: "Which setting would you prefer for a murder mystery?",
              options: [
                "An isolated country manor",
                "A bustling metropolitan city",
                "A small town where everyone knows each other",
                "An exotic location or unusual environment"
              ]
            },
            {
              id: "mystery_3",
              type: "open-ended",
              question: "Describe your ideal detective or investigator character.",
              placeholder: "Share what traits or characteristics you prefer...",
              maxLength: 300
            }
          ]
        }
      ]
    };
    
  } catch (err) {
    console.error('Error loading questionnaire:', err);
    error.value = 'Failed to load the questionnaire. Please try again.';
  } finally {
    loading.value = false;
  }
};

const handleCompletion = () => {
  submitted.value = true;
};

const navigateToDashboard = () => {
  navigateTo('/dashboard');
};
</script>
