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
    const response = await fetch(`${API_URL}/api/profiles/questionnaire`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        responses,
        timestamp: new Date().toISOString()
      })
    });
    
    if (!response.ok) {
      throw new Error('Failed to submit questionnaire');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in submitQuestionnaire:', error);
    throw error;
  }
}

/**
 * Get the user's psychological profile data
 * @returns {Promise} - User's profile data
 */
async function getUserProfile() {
  try {
    const response = await fetch(`${API_URL}/api/profiles/current`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in getUserProfile:', error);
    throw error;
  }
}

export const profileService = {
  submitQuestionnaire,
  getUserProfile
};
