/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    percySnapshot(name: string): Chainable<void>
    registerIfNeeded(email: string, password: string): Chainable<void>
  }
} 