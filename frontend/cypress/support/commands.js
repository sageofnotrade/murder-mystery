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

Cypress.Commands.add('registerIfNeeded', (email, password) => {
  cy.visit('/auth/login', { failOnStatusCode: false })
  cy.get('body').then($body => {
    if ($body.find('#email').length) {
      cy.get('#email').type(email, { force: true })
      cy.get('#password').type(password, { force: true })
      cy.get('button[type="submit"]').click({ force: true })
      cy.wait(2000)
      cy.url().then(url => {
        if (url.includes('/auth/login')) {
          // Login failed, try to register
          cy.visit('/auth/register', { failOnStatusCode: false })
          cy.get('#email').type(email, { force: true })
          cy.get('#password').type(password, { force: true })
          cy.get('#confirmPassword').type(password, { force: true })
          cy.get('button[type="submit"]').click({ force: true })
          cy.wait(2000)
        }
      })
    }
  })
}) 