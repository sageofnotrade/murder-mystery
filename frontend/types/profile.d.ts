declare module '~/stores/profileQuestionnaire' {
  import { Store } from 'pinia';
  
  interface ProfileState {
    responses: Record<string, any>;
    currentSectionIndex: number;
    isSubmitting: boolean;
    submitError: string | null;
    isCompleted: boolean;
  }

  export const useProfileQuestionnaireStore: () => Store<'profileQuestionnaire', ProfileState>;
}

declare module '~/services/profileService' {
  interface ProfileData {
    displayName?: string;
    bio?: string;
    psychological_traits?: Record<string, number>;
    preferences?: {
      difficulty?: 'easy' | 'medium' | 'hard';
      length?: 'short' | 'medium' | 'long';
    };
  }

  export const profileService: {
    getUserProfile(): Promise<ProfileData | null>;
    submitQuestionnaire(data: ProfileData): Promise<ProfileData>;
  };
} 