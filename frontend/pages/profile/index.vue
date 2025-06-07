<template>
  <div class="min-h-screen bg-mystery-dark text-gray-200 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
      <div class="bg-mystery-darker rounded-lg shadow-xl p-6 mb-8">
        <h1 class="text-3xl font-bold mb-8 text-center">Profile Setup</h1>
        
        <!-- Profile Completion Status -->
        <div class="mb-8">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold">Profile Completion</h2>
            <span class="text-mystery-accent">{{ completionPercentage }}%</span>
          </div>
          <div class="w-full bg-gray-700 rounded-full h-2.5">
            <div 
              class="bg-mystery-accent h-2.5 rounded-full transition-all duration-500"
              :style="{ width: `${completionPercentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Basic Profile Information -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Basic Information</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Display Name</label>
              <input 
                v-model="profile.displayName"
                type="text"
                class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
                placeholder="Enter your display name"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Bio</label>
              <textarea 
                v-model="profile.bio"
                rows="3"
                class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
                placeholder="Tell us about yourself..."
              ></textarea>
            </div>
          </div>
        </div>

        <!-- Psychological Profile Section -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Psychological Profile</h2>
          <div class="bg-mystery-dark rounded-lg p-4 border border-gray-700">
            <div v-if="!hasCompletedQuestionnaire" class="text-center">
              <p class="mb-4">Complete the psychological questionnaire to personalize your mystery experience.</p>
              <NuxtLink 
                to="/profile/questionnaire"
                class="inline-flex items-center px-4 py-2 bg-mystery-accent text-white rounded-md hover:bg-mystery-accent-dark transition-colors"
              >
                Start Questionnaire
              </NuxtLink>
            </div>
            <div v-else class="space-y-4">
              <div class="flex items-center justify-between">
                <span class="text-green-400">✓ Questionnaire Completed</span>
                <button 
                  @click="retakeQuestionnaire"
                  class="text-sm text-mystery-accent hover:text-mystery-accent-light"
                >
                  Retake
                </button>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div v-for="(trait, key) in psychologicalTraits" :key="key" class="bg-mystery-darker p-3 rounded">
                  <h3 class="text-sm font-medium mb-1">{{ formatTraitName(key) }}</h3>
                  <div class="w-full bg-gray-700 rounded-full h-2">
                    <div 
                      class="bg-mystery-accent h-2 rounded-full"
                      :style="{ width: `${trait * 100}%` }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Preferences Section -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold mb-4">Game Preferences</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1">Preferred Mystery Difficulty</label>
              <select 
                v-model="profile.preferences.difficulty"
                class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Preferred Mystery Length</label>
              <select 
                v-model="profile.preferences.length"
                class="w-full px-3 py-2 bg-mystery-dark border border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-mystery-accent"
              >
                <option value="short">Short (30-60 minutes)</option>
                <option value="medium">Medium (1-2 hours)</option>
                <option value="long">Long (2+ hours)</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Save Button -->
        <div class="flex justify-end">
          <button 
            @click="saveProfile"
            class="px-6 py-2 bg-mystery-accent text-white rounded-md hover:bg-mystery-accent-dark transition-colors"
            :disabled="isSaving"
          >
            {{ isSaving ? 'Saving...' : 'Save Profile' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useProfileQuestionnaireStore } from '~/stores/profileQuestionnaire';
import { profileService } from '~/services/profileService';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useProfileQuestionnaireStore();

const profile = ref({
  displayName: '',
  bio: '',
  preferences: {
    difficulty: 'medium',
    length: 'medium'
  }
});

const isSaving = ref(false);
const hasCompletedQuestionnaire = ref(false);
const psychologicalTraits = ref({});

const completionPercentage = computed(() => {
  let completed = 0;
  let total = 3; // Basic info, questionnaire, preferences

  if (profile.value.displayName) completed++;
  if (hasCompletedQuestionnaire.value) completed++;
  if (profile.value.preferences.difficulty && profile.value.preferences.length) completed++;

  return Math.round((completed / total) * 100);
});

onMounted(async () => {
  try {
    const userProfile = await profileService.getUserProfile();
    if (userProfile) {
      profile.value = {
        ...profile.value,
        ...userProfile,
        preferences: {
          ...profile.value.preferences,
          ...userProfile.preferences
        }
      };
      hasCompletedQuestionnaire.value = !!userProfile.psychological_traits;
      psychologicalTraits.value = userProfile.psychological_traits || {};
    }
  } catch (error) {
    console.error('Error loading profile:', error);
  }
});

const formatTraitName = (trait: string) => {
  return trait
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

const retakeQuestionnaire = () => {
  store.resetQuestionnaire();
  router.push('/profile/questionnaire');
};

const saveProfile = async () => {
  try {
    isSaving.value = true;
    await profileService.submitQuestionnaire({
      ...profile.value,
      psychological_traits: psychologicalTraits.value
    });
    // Show success message or handle navigation
  } catch (error) {
    console.error('Error saving profile:', error);
    // Show error message
  } finally {
    isSaving.value = false;
  }
};
</script> 