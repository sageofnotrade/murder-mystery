/**
 * Profile Service
 * Handles API interactions related to user psychological profiles
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

/**
 * Submit psychological questionnaire responses to the backend
 * @param {Object} responses - The questionnaire responses keyed by question ID
 * @returns {Promise} - API response with profile data
 */
async function submitQuestionnaire(responses) {
  try {
    const { data, error } = await useFetch(`${API_URL}/api/profiles/questionnaire`, {
      method: 'POST',
      body: {
        responses,
        timestamp: new Date().toISOString()
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (error.value) {
      throw new Error(error.value.statusMessage || 'Failed to submit questionnaire');
    }
    
    return data.value;
  } catch (err) {
    console.error('Error in submitQuestionnaire:', err);
    throw err;
  }
}

/**
 * Get the user's psychological profile data
 * @returns {Promise} - User's profile data
 */
async function getUserProfile() {
  try {
    const { data, error } = await useFetch(`${API_URL}/api/profiles/current`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (error.value) {
      throw new Error(error.value.statusMessage || 'Failed to fetch profile');
    }
    
    return data.value;
  } catch (err) {
    console.error('Error in getUserProfile:', err);
    throw err;
  }
}

export const profileService = {
  submitQuestionnaire,
  getUserProfile
};
