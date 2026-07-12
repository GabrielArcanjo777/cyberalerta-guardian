import {test, expect} from '@playwright/test'

/**
 * Set the motion preference in localStorage BEFORE navigation so the
 * anti-flash script picks it up and applies data-motion to <html>.
 */
async function setMotionPref(page: import('@playwright/test').Page, pref: 'enabled' | 'reduced' | 'system') {
  await page.addInitScript((p) => {
    window.localStorage.setItem('cyberalerta-motion-preference', p)
  }, pref)
}

test.describe('Hero animation', () => {

  test('enabled + system reduce: animation runs despite OS setting', async ({page}) => {
    await setMotionPref(page, 'enabled')
    await page.emulateMedia({reducedMotion: 'reduce'})
    await page.goto('/')
    await page.waitForTimeout(300)

    const inner = page.locator('[class*="titleLineInner"]')
    expect(await inner.count()).toBe(3)

    for (let i = 0; i < 3; i++) {
      const el = inner.nth(i)
      const animName = await el.evaluate(node => getComputedStyle(node).animationName)
      expect(animName).not.toBe('none')
      expect(animName).not.toBe('')
    }

    // After animation completes, check final state
    await page.waitForTimeout(2000)
    for (let i = 0; i < 3; i++) {
      const el = inner.nth(i)
      expect(await el.evaluate(n => getComputedStyle(n).opacity)).toBe('1')
    }
  })

  test('reduced: animation disabled', async ({page}) => {
    await setMotionPref(page, 'reduced')
    await page.goto('/')
    await page.waitForTimeout(300)

    const inner = page.locator('[class*="titleLineInner"]')
    expect(await inner.count()).toBe(3)

    for (let i = 0; i < 3; i++) {
      const el = inner.nth(i)
      const animName = await el.evaluate(node => getComputedStyle(node).animationName)
      expect(['none', '']).toContain(animName)
      expect(await el.evaluate(n => getComputedStyle(n).opacity)).toBe('1')
    }
  })

  test('system + OS no-preference: animation runs', async ({page}) => {
    await setMotionPref(page, 'system')
    await page.emulateMedia({reducedMotion: 'no-preference'})
    await page.goto('/')
    await page.waitForTimeout(300)

    const inner = page.locator('[class*="titleLineInner"]')
    for (let i = 0; i < 3; i++) {
      const animName = await inner.nth(i).evaluate(node => getComputedStyle(node).animationName)
      expect(animName).not.toBe('none')
    }
  })

  test('system + OS reduce: animation disabled', async ({page}) => {
    await setMotionPref(page, 'system')
    await page.emulateMedia({reducedMotion: 'reduce'})
    await page.goto('/')
    await page.waitForTimeout(300)

    const inner = page.locator('[class*="titleLineInner"]')
    for (let i = 0; i < 3; i++) {
      const animName = await inner.nth(i).evaluate(node => getComputedStyle(node).animationName)
      expect(['none', '']).toContain(animName)
    }
  })

  test('persistence: enabled survives reload', async ({page}) => {
    await setMotionPref(page, 'enabled')
    await page.emulateMedia({reducedMotion: 'reduce'})
    await page.goto('/')
    await page.waitForTimeout(300)

    // First load — animation runs
    let animName = await page.locator('[class*="titleLineInner"]').first().evaluate(node => getComputedStyle(node).animationName)
    expect(animName).not.toBe('none')

    // Reload — still enabled
    await page.reload()
    await page.waitForTimeout(300)
    animName = await page.locator('[class*="titleLineInner"]').first().evaluate(node => getComputedStyle(node).animationName)
    expect(animName).not.toBe('none')
  })
})