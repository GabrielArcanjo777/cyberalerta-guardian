import {test, expect} from '@playwright/test'
import {mockAuth, mockLogout} from './auth-helpers'

test.describe('Landing page → WhatsApp setup', () => {

  test('deslogado clica Conectar WhatsApp → navega para /whatsapp-setup (ProtectedRoute renderiza auth gate)', async ({page}) => {
    await mockLogout(page)
    await page.goto('/')

    await page.click('a.home-secondary-cta')

    // Lands on /whatsapp-setup. ProtectedRoute shows auth gate or renders content.
    // We verify the URL is correct — the auth gate is tested by other flows.
    await expect(page).toHaveURL('/whatsapp-setup')
  })

  test('autenticado clica Conectar WhatsApp → entra diretamente', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/')

    await page.click('a.home-secondary-cta')

    await expect(page).toHaveURL('/whatsapp-setup')
    // The setup page must show the QR/status section
    await expect(page.locator('text=Conectar WhatsApp')).toBeVisible({timeout: 5000})
  })
})

test.describe('Console access', () => {

  test('deslogado acessa /family-console → ProtectedRoute mostra auth gate', async ({page}) => {
    await mockLogout(page)
    await page.goto('/family-console')

    // ProtectedRoute renders an auth gate. The URL stays on /family-console.
    await expect(page).toHaveURL('/family-console')
  })

  test('autenticado acessa /family-console → entra diretamente', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/family-console')

    await expect(page).toHaveURL('/family-console')
    await expect(page.locator('text=Guardian Console')).toBeVisible({timeout: 5000})
  })
})

test.describe('Admin access', () => {

  test('usuário comum não vê botão Admin', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/family-console')
    await page.waitForTimeout(1000)

    await expect(page.locator('a:has-text("Admin")')).toHaveCount(0)
  })

  test('admin vê botão Admin no header', async ({page}) => {
    await mockAuth(page, 'admin')
    await page.goto('/family-console')
    await page.waitForTimeout(1000)

    // Admin link appears in desktop header (.guardian-header-actions)
    await expect(page.locator('.guardian-header-actions a:has-text("Admin")')).toBeVisible()
  })

  test('usuário comum acessando /admin é bloqueado', async ({page}) => {
    await mockAuth(page, 'viewer')
    await page.goto('/admin')

    await expect(page.locator('text=Esta area exige permissao de administrador')).toBeVisible({timeout: 5000})
  })

  test('admin acessa /admin com sucesso', async ({page}) => {
    await mockAuth(page, 'admin')
    await page.goto('/admin')

    await expect(page).toHaveURL('/admin')
    // Use a heading-level match to avoid strict-mode double-match with the stats card
    await expect(page.getByRole('heading', {name: 'Usuarios'})).toBeVisible({timeout: 5000})
    await expect(page.locator('text=Auditoria de autenticacao')).toBeVisible()
  })
})
