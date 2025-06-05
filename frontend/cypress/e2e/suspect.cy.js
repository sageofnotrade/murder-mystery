describe('Suspect Interactions', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123')
    cy.createNewGame()
  })

  it('should interact with suspects and record responses', () => {
    // Talk to a suspect
    cy.talkToSuspect('butler')
    
    // Ask questions
    cy.get('[data-cy="question-input"]').type('Where were you at the time of the murder?')
    cy.get('[data-cy="ask-question"]').click()
    
    // Verify response
    cy.get('[data-cy="suspect-response"]').should('be.visible')
    
    // Record response on board
    cy.get('[data-cy="add-to-board"]').click()
    cy.get('[data-cy="board-element"]').should('contain', 'butler')
  })

  it('should handle suspect mood changes', () => {
    // Talk to suspect
    cy.talkToSuspect('maid')
    
    // Ask aggressive question
    cy.get('[data-cy="question-input"]').type('Did you kill the victim?')
    cy.get('[data-cy="ask-question"]').click()
    
    // Verify mood change
    cy.get('[data-cy="suspect-mood"]').should('have.class', 'angry')
    
    // Verify dialogue options change
    cy.get('[data-cy="dialogue-options"]').should('not.contain', 'friendly')
  })
}) 