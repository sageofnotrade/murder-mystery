import { defineNuxtRouteMiddleware, navigateTo, useCookie } from '#app'

export default defineNuxtRouteMiddleware((to) => {
  const publicRoutes = ['/auth/login', '/auth/register', '/auth/callback', '/']
  
  // Skip middleware for public routes
  if (publicRoutes.includes(to.path)) {
    return
  }

  // Check if we have a token in localStorage
  const token = useCookie('auth_token').value
  
  if (!token) {
    // Redirect to login if no token is found
    return navigateTo('/auth/login')
  }
}) 