import { defineStore } from 'pinia'
import { profileService } from '~/services/profileService'
// @ts-expect-error: missing types from pinia-plugin-persistedstate
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

export const useProfileQuestionnaireStore = defineStore('profileQuestionnaire', {
  state: () => ({
    responses: {} as Record<string, any>,
    currentSectionIndex: 0,
    isSubmitting: false,
    submitError: null as string | null,
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

        // Submit responses to API
        await profileService.submitQuestionnaire(this.responses);

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
