import {Page} from '@playwright/test'

type Role = 'viewer' | 'analyst' | 'admin'

interface AuthUser {
  id: string
  email: string
  full_name: string
  role: Role
  is_admin: boolean
  mfa_enabled: boolean
}

const USERS: Record<Role, AuthUser> = {
  viewer: {id: 'user-viewer', email: 'comum@teste.local', full_name: 'Usuário Comum', role: 'viewer', is_admin: false, mfa_enabled: false},
  analyst: {id: 'user-analyst', email: 'analista@teste.local', full_name: 'Analista', role: 'analyst', is_admin: false, mfa_enabled: false},
  admin: {id: 'user-admin', email: 'admin@teste.local', full_name: 'Administrador', role: 'admin', is_admin: true, mfa_enabled: true},
}

/**
 * Mock the /auth/me response so the frontend believes `role` is authenticated.
 * Call `mockLogout` to revert to unauthenticated state.
 */
export async function mockAuth(page: Page, role: Role): Promise<void> {
  const user = USERS[role]
  await page.route('**/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({user}),
    })
  })
}

/**
 * Mock /auth/me to return 401 (unauthenticated).
 * Also clears cookies to ensure no real session leaks in.
 */
export async function mockLogout(page: Page): Promise<void> {
  await page.context().clearCookies()
  await page.route('**/auth/me', async (route) => {
    await route.fulfill({status: 401, contentType: 'application/json', body: '{"detail":"Unauthorized"}'})
  })
}

export {USERS}
