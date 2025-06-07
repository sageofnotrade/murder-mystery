describe('Game Flow', () => {
  beforeEach(() => {
    cy.registerIfNeeded('test@example.com', 'password123')
    cy.wait(1000)
    cy.visit('/mystery/board', { failOnStatusCode: false })
    cy.wait(2000)
  })

  it('should create a new game', () => {
    cy.contains('New Game').click({ force: true })
    cy.get('form').should('be.visible')
    cy.get('input[name="title"]').type('Test Game')
    cy.get('textarea[name="description"]').type('Test Description')
    cy.get('button[type="submit"]').click({ force: true })
    cy.wait(2000)
    cy.url().should('include', '/mystery/board')
    cy.percySnapshot('New Game Created')
  })

  it('should show game details', () => {
    cy.contains('Test Game').click({ force: true })
    cy.get('.game-details').should('be.visible')
    cy.get('.game-details').should('contain', 'Test Description')
    cy.percySnapshot('Game Details')
  })

  it('should interact with clues', () => {
    cy.contains('Add Clue').click({ force: true })
    cy.get('form').should('be.visible')
    cy.get('input[name="title"]').type('Test Clue')
    cy.get('textarea[name="description"]').type('Test Clue Description')
    cy.get('button[type="submit"]').click({ force: true })
    cy.wait(2000)
    cy.contains('Test Clue').should('be.visible')
    cy.percySnapshot('Clue Added')
  })
}) 