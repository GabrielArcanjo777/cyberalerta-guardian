import {test, expect} from '@playwright/test'
import {mockAuth} from './auth-helpers'

/**
 * Open-redirect / redirect sanitization tests.
 *
 * Strategy: mock auth as a viewer, navigate to /login?redirect=<value>,
 * then verify that the page auto-redirects to /family-console (the safe
 * default) instead of any malicious destination.
 */
test.describe('Open redirect protection', () => {

  const MALICIOUS = [
    'https://evil.com',
    'http://evil.com',
    '//evil.com',
    '/%5cevil.com',
    '%2F%2Fevil.com',
    '%252F%252Fevil.com',
    'javascript:alert(1)',
    '/rota-inexistente',
  ]

  for (const redirect of MALICIOUS) {
    test(`redirect rejeitado: ${redirect} → fallback /family-console`, async ({page}) => {
      await mockAuth(page, 'viewer')

      // Navigate to login with the malicious redirect. The already-authenticated
      // user should be forwarded to the safe DEFAULT_REDIRECT, never the malicious one.
      await page.goto(`/login?redirect=${encodeURIComponent(redirect)}`)

      // The login page's getAuthMe useEffect will redirect us.
      // We must end up at /family-console — never the malicious URL.
      await expect(page).toHaveURL('/family-console', {timeout: 5000})
    })
  }

  test('redirect legitimo /family-console funciona', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/login?redirect=%2Ffamily-console')
    await expect(page).toHaveURL('/family-console', {timeout: 5000})
  })

  test('redirect legitimo /whatsapp-setup funciona', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/login?redirect=%2Fwhatsapp-setup')
    await expect(page).toHaveURL('/whatsapp-setup', {timeout: 5000})
  })

  test('redirect legitimo /admin funciona (redireciona, mas AdminRoute bloqueia)', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/login?redirect=%2Fadmin')
    // Forwarded to /admin, but AdminRoute blocks non-admin
    await expect(page).toHaveURL('/admin', {timeout: 5000})
    await expect(page.locator('text=Esta area exige permissao de administrador')).toBeVisible({timeout: 5000})
  })

  test('sem redirect → fallback /family-console', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/login')
    await expect(page).toHaveURL('/family-console', {timeout: 5000})
  })
})
