# Team Member 1 - Milestone 2 Task Guide

## Your Tasks Overview

| Task ID | Title | Estimate | Dependencies |
|---------|-------|----------|-------------|
| FE-004 | Create psychological profile questionnaire UI | 6h | FE-003 |
| BE-004 | Create mystery template storage and retrieval | 6h | BE-001 |
| **Total** | | **12h** | |

## Task Details and Implementation Guide

### FE-004: Create psychological profile questionnaire UI

#### Description
Create a user interface for collecting psychological profile information from users. This questionnaire will be used to tailor the murder mystery experience to the user's psychological traits and preferences.

#### Implementation Steps

1. **Review existing authentication UI (FE-003)**
   - Examine the existing authentication UI to maintain design consistency
   - Note the styling patterns and component structure

2. **Design the questionnaire structure**
   - Create a multi-step form with progress indicators
   - Plan for 5-7 psychological trait categories with 3-5 questions each
   - Include a mix of multiple-choice, slider, and open-ended questions

3. **Implement Vue components**
   ```bash
   # Create the main questionnaire component
   touch frontend/components/profile/PsychologicalQuestionnaire.vue
   # Create individual question type components
   touch frontend/components/profile/MultipleChoiceQuestion.vue
   touch frontend/components/profile/SliderQuestion.vue
   touch frontend/components/profile/OpenEndedQuestion.vue
   ```

4. **Implement the questionnaire page**
   ```bash
   # Create the questionnaire page
   touch frontend/pages/profile/questionnaire.vue
   ```

5. **Create Pinia store for questionnaire state**
   ```bash
   # Create store for questionnaire data
   touch frontend/stores/profileQuestionnaire.js
   ```

6. **Implement form validation**
   - Use Vuelidate or similar for form validation
   - Ensure all required questions are answered before proceeding

7. **Create API service for submitting questionnaire data**
   ```bash
   # Create API service
   touch frontend/services/profileService.js
   ```

8. **Implement responsive design**
   - Ensure the questionnaire works well on mobile, tablet, and desktop

9. **Add loading and success states**
   - Show loading indicators during submission
   - Display success message upon completion

#### Example Questionnaire Structure

```javascript
// Sample questionnaire structure
const questionnaire = {
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
        // More questions...
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
        // More questions...
      ]
    },
    // More sections...
  ]
};
```

#### Resources
- [Vue.js Forms Guide](https://vuejs.org/guide/essentials/forms.html)
- [Tailwind CSS Forms](https://tailwindcss.com/docs/plugins#forms)
- [Pinia State Management](https://pinia.vuejs.org/core-concepts/)
- [Nuxt.js Pages](https://nuxt.com/docs/guide/directory-structure/pages)

---

### BE-004: Create mystery template storage and retrieval

#### Description
Implement backend functionality to store, retrieve, and manage mystery templates. These templates will be used by the AI agents to generate personalized murder mysteries.

#### Implementation Steps

1. **Review Flask project structure (BE-001)**
   - Understand the existing Flask application structure
   - Note the patterns used for routes and controllers

2. **Design the mystery template data model**
   - Create a Pydantic model for mystery templates
   - Ensure compatibility with Supabase storage

3. **Implement database schema in Supabase**
   - Create necessary tables for mystery templates
   - Set up appropriate relationships and indexes

4. **Create Flask routes for template management**
   ```bash
   # Create template routes file
   touch backend/routes/template_routes.py
   ```

5. **Implement CRUD operations for templates**
   - Create: Add new mystery templates
   - Read: Retrieve templates by ID or query parameters
   - Update: Modify existing templates
   - Delete: Remove templates

6. **Add template validation**
   - Use Pydantic for input validation
   - Ensure templates follow the required structure

7. **Implement template versioning**
   - Add support for template versions
   - Allow retrieving specific versions

8. **Create service layer for template operations**
   ```bash
   # Create template service
   touch backend/services/template_service.py
   ```

9. **Add authentication and authorization**
   - Ensure only authorized users can manage templates
   - Implement role-based access control

10. **Write unit tests**
    ```bash
    # Create test file
    touch backend/tests/test_template_routes.py
    ```

#### Example Template Model

```python
# Example Pydantic model for mystery templates
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union, Literal

class Suspect(BaseModel):
    name: str
    description: str
    motive: str
    alibi: str
    guilty: bool = False
    personality_traits: Dict[str, float] = Field(default_factory=dict)
    
class Clue(BaseModel):
    id: str
    description: str
    location: str
    related_suspects: List[str] = Field(default_factory=list)
    discovery_difficulty: float = 1.0
    type: Literal["physical", "testimony", "observation", "document"] 
    
class MysteryTemplate(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    setting: str
    time_period: str
    victim: Dict[str, str]
    suspects: List[Suspect]
    clues: List[Clue]
    red_herrings: List[Dict[str, str]] = Field(default_factory=list)
    difficulty: float = 1.0
    estimated_duration: str = "1 hour"
    version: str = "1.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_by: Optional[str] = None
```

#### Example API Endpoints

```
GET /api/templates - List all templates
GET /api/templates/{id} - Get a specific template
POST /api/templates - Create a new template
PUT /api/templates/{id} - Update a template
DELETE /api/templates/{id} - Delete a template
```

#### Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [RESTful API Design](https://restfulapi.net/)

## Testing Your Work

### FE-004 Testing
1. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
2. Navigate to the questionnaire page
3. Test all question types and form validation
4. Verify mobile responsiveness using browser dev tools
5. Test form submission and error handling

### BE-004 Testing
1. Run the Flask development server:
   ```bash
   cd backend
   flask run
   ```
2. Use Postman or curl to test API endpoints:
   ```bash
   # Example: Get all templates
   curl -X GET http://localhost:5000/api/templates
   
   # Example: Create a template
   curl -X POST http://localhost:5000/api/templates \
     -H "Content-Type: application/json" \
     -d '{"title": "Test Template", ...}'
   ```
3. Run unit tests:
   ```bash
   cd backend
   pytest tests/test_template_routes.py
   ```

## Deliverables

### FE-004 Deliverables
- Complete questionnaire UI components
- Pinia store for questionnaire state
- API service for submitting data
- Responsive design for all device sizes

### BE-004 Deliverables
- Mystery template Pydantic models
- Flask routes for template CRUD operations
- Supabase integration for template storage
- Unit tests for all endpoints

## Communication

If you encounter any blockers or have questions:
- Post in the #milestone-2 Slack channel
- Tag the project lead for urgent issues
- Document any design decisions or assumptions in your PR description

Good luck with your tasks! Remember to commit your work regularly and create pull requests for review.
