// Custom command to login
Cypress.Commands.add('login', (email, password) => {
  cy.visit('/login')
  cy.get('[data-cy="email-input"]').type(email)
  cy.get('[data-cy="password-input"]').type(password)
  cy.get('[data-cy="login-button"]').click()
})

// Custom command to create a new game
Cypress.Commands.add('createNewGame', () => {
  cy.get('[data-cy="new-game-button"]').click()
  cy.get('[data-cy="confirm-new-game"]').click()
})

// Custom command to interact with the board
Cypress.Commands.add('addBoardElement', (type, content) => {
  cy.get(`[data-cy="add-${type}"]`).click()
  cy.get('[data-cy="element-content"]').type(content)
  cy.get('[data-cy="save-element"]').click()
})

// Custom command to interact with suspects
Cypress.Commands.add('talkToSuspect', (suspectName) => {
  cy.get(`[data-cy="suspect-${suspectName}"]`).click()
  cy.get('[data-cy="start-conversation"]').click()
})

// Custom command to check game state
Cypress.Commands.add('checkGameState', (expectedState) => {
  cy.get('[data-cy="game-state"]').should('have.text', expectedState)
}) 