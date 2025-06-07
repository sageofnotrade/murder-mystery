describe('Authentication', () => {
  beforeEach(() => {
    cy.registerIfNeeded('test@example.com', 'password123')
    cy.wait(1000) // Wait for app to load
  })

  it('should show login form', () => {
    cy.visit('/auth/login', { failOnStatusCode: false })
    cy.get('form').should('be.visible')
    cy.get('#email').should('be.visible')
    cy.get('#password').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
    cy.percySnapshot('Login Form')
  })

  it('should show registration form', () => {
    cy.visit('/auth/login', { failOnStatusCode: false })
    cy.contains('Sign Up').click({ force: true })
    cy.url().should('include', '/auth/register')
    cy.get('form').should('be.visible')
    cy.get('#email').should('be.visible')
    cy.get('#password').should('be.visible')
    cy.get('#confirmPassword').should('be.visible')
    cy.percySnapshot('Registration Form')
  })

  it('should handle login', () => {
    cy.visit('/auth/login', { failOnStatusCode: false })
    cy.get('#email').type('test@example.com', { force: true })
    cy.get('#password').type('password123', { force: true })
    cy.get('button[type="submit"]').click({ force: true })
    cy.wait(2000)
    cy.url().should('include', '/dashboard')
    cy.get('h1').should('contain', 'Welcome to Your Mystery')
    cy.percySnapshot('Dashboard After Login')
  })
}) 