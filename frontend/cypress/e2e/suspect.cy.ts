describe('Suspect Management', () => {
  beforeEach(() => {
    cy.registerIfNeeded('test@example.com', 'password123')
    cy.wait(1000)
    cy.visit('/mystery/board', { failOnStatusCode: false })
    cy.wait(2000)
  })

  it('should show suspect list', () => {
    cy.contains('Suspects').click({ force: true })
    cy.get('.suspect-list').should('be.visible')
    cy.percySnapshot('Suspect List')
  })

  it('should show suspect details', () => {
    cy.contains('Add Suspect').click({ force: true })
    cy.get('form').should('be.visible')
    cy.get('input[name="name"]').type('Test Suspect')
    cy.get('textarea[name="description"]').type('Test Suspect Description')
    cy.get('button[type="submit"]').click({ force: true })
    cy.wait(2000)
    cy.contains('Test Suspect').should('be.visible')
    cy.percySnapshot('Suspect Added')
  })

  it('should handle suspect questioning', () => {
    cy.contains('Test Suspect').click({ force: true })
    cy.get('.suspect-details').should('be.visible')
    cy.get('.suspect-details').should('contain', 'Test Suspect Description')
    cy.percySnapshot('Suspect Details')
  })
}) 