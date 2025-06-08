import { defineStore } from 'pinia'
import { profileService } from '~/services/profileService'
// @ts-expect-error: missing types from pinia-plugin-persistedstate
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

interface ProfileState {
  responses: Record<string, any>;
  currentSectionIndex: number;
  isSubmitting: boolean;
  submitError: string | null;
  isCompleted: boolean;
}

export const useProfileQuestionnaireStore = defineStore('profileQuestionnaire', {
  state: (): ProfileState => ({
    responses: {},
    currentSectionIndex: 0,
    isSubmitting: false,
    submitError: null,
    isCompleted: false
  }),

  actions: {
    updateResponses(responses: Record<string, any>) {
      this.responses = { ...responses };
    },

    updateCurrentSectionIndex(index: number) {
      this.currentSectionIndex = index;
    },

    async submitResponses(): Promise<boolean> {
      try {
        this.isSubmitting = true;
        this.submitError = null;
        this.isCompleted = true;
        return true;
      } catch (error: any) {
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
      this.isCompleted = false;
    }
  },

});
