import { defineStore } from 'pinia';
import { profileService } from '~/services/profileService';

export const useProfileQuestionnaireStore = defineStore('profileQuestionnaire', {
  state: () => ({
    responses: {},
    currentSectionIndex: 0,
    isSubmitting: false,
    submitError: null,
    isCompleted: false
  }),
  
  actions: {
    updateResponses(responses) {
      this.responses = { ...responses };
    },
    
    updateCurrentSectionIndex(index) {
      this.currentSectionIndex = index;
    },
    
    async submitResponses() {
      try {
        this.isSubmitting = true;
        this.submitError = null;
        
        // Submit responses to API
        await profileService.submitQuestionnaire(this.responses);
        
        this.isCompleted = true;
        return true;
      } catch (error) {
        console.error('Error submitting questionnaire:', error);
        this.submitError = error.message || 'Failed to submit questionnaire';
        throw error;
      } finally {
        this.isSubmitting = false;
      }
    },
    
    resetQuestionnaire() {
      this.responses = {};
      this.currentSectionIndex = 0;
      this.isSubmitting = false;
      this.submitError = null;
    }
  },
  
  persist: {
    storage: persistedState.localStorage,
    paths: ['responses', 'currentSectionIndex']
  }
});
