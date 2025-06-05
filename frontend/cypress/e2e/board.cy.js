describe('Detective Board Interactions', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123')
    cy.createNewGame()
  })

  it('should add and connect board elements', () => {
    // Add a clue
    cy.addBoardElement('clue', 'Bloody knife found in kitchen')
    
    // Add a suspect
    cy.addBoardElement('suspect', 'John Doe')
    
    // Add a location
    cy.addBoardElement('location', 'Kitchen')
    
    // Connect elements
    cy.get('[data-cy="connect-elements"]').click()
    cy.get('[data-cy="element-1"]').drag('[data-cy="element-2"]')
    cy.get('[data-cy="save-connection"]').click()
    
    // Verify connection
    cy.get('[data-cy="connection"]').should('be.visible')
  })

  it('should save and load board state', () => {
    // Add elements
    cy.addBoardElement('clue', 'Test clue')
    cy.addBoardElement('suspect', 'Test suspect')
    
    // Save board
    cy.get('[data-cy="save-board"]').click()
    
    // Reload page
    cy.reload()
    
    // Verify elements are still there
    cy.get('[data-cy="element"]').should('have.length', 2)
  })
}) 