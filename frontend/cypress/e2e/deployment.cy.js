// E2E Deployment & Polish Tests
// Covers: deployment health, error boundaries, UI polish, edge/failure cases

const urls = [
  'http://localhost:3000',
  'https://staging.murthra.app', // Replace with actual staging URL
  'https://murthra.app' // Replace with actual production URL
];

describe('Deployment Health & Polish', () => {
  urls.forEach((baseUrl) => {
    context(`Environment: ${baseUrl}`, () => {
      beforeEach(() => {
        cy.visit(baseUrl);
      });

      it('should load the main app shell', () => {
        cy.get('body').should('be.visible');
        cy.get('[data-cy="main-app"]').should('exist');
      });

      it('should show login page and handle login errors', () => {
        cy.get('[data-cy="email-input"]').type('baduser@example.com');
        cy.get('[data-cy="password-input"]').type('wrongpassword');
        cy.get('[data-cy="login-button"]').click();
        cy.get('[data-cy="login-error"]').should('be.visible');
      });

      it('should be responsive on mobile', () => {
        cy.viewport('iphone-6');
        cy.get('[data-cy="main-app"]').should('be.visible');
      });

      it('should handle network/API failure gracefully', () => {
        cy.intercept('POST', '/api/*', { forceNetworkError: true }).as('apiFail');
        cy.get('[data-cy="login-button"]').click();
        cy.get('[data-cy="error-boundary"]').should('be.visible');
      });
    });
  });
});
