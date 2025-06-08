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
    
    // Murder Mystery Big Five Personality Questionnaire
    questionnaire.value = {
      sections: [
        {
          title: "🧠 Openness (Imagination, Curiosity, Aesthetics)",
          description: "Answer the following as truthfully as you dare... the mystery depends on it.",
          questions: [
            {
              id: "openness_1",
              type: "slider",
              question: "I enjoy unraveling complex puzzles or riddles, even if there's no reward.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "openness_2",
              type: "slider",
              question: "I find myself imagining alternate endings to stories—especially murders.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "openness_3",
              type: "slider",
              question: "I enjoy exploring strange theories and possibilities, no matter how wild.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "openness_4",
              type: "slider",
              question: "A quirky, eccentric character usually catches my attention more than a traditional hero.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "openness_5",
              type: "slider",
              question: "I often notice tiny details that others overlook, even in chaotic situations.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "📋 Conscientiousness (Organization, Discipline, Duty)",
          description: "How do you approach tasks and responsibilities?",
          questions: [
            {
              id: "conscientiousness_1",
              type: "slider",
              question: "I prefer having a clear plan before taking action, especially under pressure.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "conscientiousness_2",
              type: "slider",
              question: "I take notes and keep records, even when others call it \"obsessive.\"",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "conscientiousness_3",
              type: "slider",
              question: "I feel a strong need to see tasks through to the end—even in the face of danger.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "conscientiousness_4",
              type: "slider",
              question: "I get frustrated when others act recklessly or break the rules.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "conscientiousness_5",
              type: "slider",
              question: "I double-check clues and facts before jumping to conclusions.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "🎭 Extraversion (Sociability, Energy, Boldness)",
          description: "How do you interact with others and handle social situations?",
          questions: [
            {
              id: "extraversion_1",
              type: "slider",
              question: "I feel energized when I talk to new people, even potential suspects.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "extraversion_2",
              type: "slider",
              question: "I would volunteer to question a shady character without hesitation.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "extraversion_3",
              type: "slider",
              question: "I enjoy being in the center of the action—even in dramatic or tense scenes.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "extraversion_4",
              type: "slider",
              question: "I tend to act on instinct in the heat of the moment.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "extraversion_5",
              type: "slider",
              question: "I prefer working with a group over investigating alone.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "🤝 Agreeableness (Empathy, Cooperation, Compassion)",
          description: "How do you approach relationships and conflicts?",
          questions: [
            {
              id: "agreeableness_1",
              type: "slider",
              question: "I often give people the benefit of the doubt—even if they look suspicious.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "agreeableness_2",
              type: "slider",
              question: "I try to keep the peace, even if it means sacrificing my own theory.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "agreeableness_3",
              type: "slider",
              question: "I feel bad accusing someone without solid evidence.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "agreeableness_4",
              type: "slider",
              question: "I'm more interested in understanding motives than just finding \"whodunit.\"",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "agreeableness_5",
              type: "slider",
              question: "I would help a fellow detective cover a mistake to spare them embarrassment.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            }
          ]
        },
        {
          title: "🌀 Neuroticism (Emotional Stability, Anxiety, Sensitivity)",
          description: "How do you handle stress and emotional challenges?",
          questions: [
            {
              id: "neuroticism_1",
              type: "slider",
              question: "I often second-guess myself after making a decision.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "neuroticism_2",
              type: "slider",
              question: "I get nervous when the pressure is on—even if I'm sure I'm right.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "neuroticism_3",
              type: "slider",
              question: "I take things personally when suspects lie or hide the truth.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "neuroticism_4",
              type: "slider",
              question: "I sometimes lose sleep over mysteries left unsolved.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
            },
            {
              id: "neuroticism_5",
              type: "slider",
              question: "I worry about missing something obvious and looking like a fool.",
              min: 1,
              max: 5,
              minLabel: "Strongly Disagree",
              maxLabel: "Strongly Agree"
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
