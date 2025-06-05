describe('Complete Game Flow', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123')
  })

  it('should complete a full game cycle', () => {
    // Start new game
    cy.createNewGame()
    
    // Check initial game state
    cy.checkGameState('investigation')
    
    // Explore locations
    cy.get('[data-cy="location-kitchen"]').click()
    cy.get('[data-cy="search-location"]').click()
    cy.get('[data-cy="clue-found"]').should('be.visible')
    
    // Talk to suspects
    cy.talkToSuspect('butler')
    cy.get('[data-cy="question-input"]').type('What did you see?')
    cy.get('[data-cy="ask-question"]').click()
    
    // Add evidence to board
    cy.addBoardElement('clue', 'Butler was in the kitchen')
    cy.addBoardElement('suspect', 'Butler')
    cy.get('[data-cy="connect-elements"]').click()
    cy.get('[data-cy="element-1"]').drag('[data-cy="element-2"]')
    
    // Make accusation
    cy.get('[data-cy="make-accusation"]').click()
    cy.get('[data-cy="select-suspect"]').select('butler')
    cy.get('[data-cy="select-motive"]').select('revenge')
    cy.get('[data-cy="submit-accusation"]').click()
    
    // Verify game end
    cy.checkGameState('completed')
    cy.get('[data-cy="game-result"]').should('be.visible')
  })

  it('should handle game progression correctly', () => {
    cy.createNewGame()
    
    // Verify tutorial appears for new game
    cy.get('[data-cy="tutorial"]').should('be.visible')
    cy.get('[data-cy="close-tutorial"]').click()
    
    // Check game milestones
    cy.get('[data-cy="milestone-1"]').should('be.visible')
    cy.addBoardElement('clue', 'First clue')
    cy.get('[data-cy="milestone-1"]').should('have.class', 'completed')
    
    // Verify game saves progress
    cy.get('[data-cy="save-game"]').click()
    cy.reload()
    cy.get('[data-cy="milestone-1"]').should('have.class', 'completed')
  })
}) 