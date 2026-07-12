/**
 * Safe redirect validation for post-authentication forwarding.
 *
 * Only internal application paths are allowed. The validator rejects:
 * - absolute URLs (http:, https:, javascript:, data:, etc.)
 * - protocol-relative URLs (//evil.com)
 * - backslash tricks (/\evil.com)
 * - double-encoded bypasses
 * - any path not in the explicit allowlist.
 */

const ALLOWED_REDIRECT_ROUTES = new Set([
  '/family-console',
  '/whatsapp-setup',
  '/admin',
  '/mfa',
  '/login',
])

/** Default destination when the redirect param is missing or invalid. */
export const DEFAULT_REDIRECT = '/family-console'

/**
 * Safely decode a URL component, catching malformed sequences.
 * Returns null on failure — the caller must fall back to DEFAULT_REDIRECT.
 */
function safeDecode(raw: string): string | null {
  try {
    return decodeURIComponent(raw)
  } catch {
    return null
  }
}

/**
 * Validate and normalize a user-supplied redirect parameter.
 *
 * @param value  Raw query-string value (may be null, encoded, or malicious).
 * @returns      A safe internal path, or null if the value is invalid.
 */
export function sanitizeAuthRedirect(value: string | null | undefined): string | null {
  if (!value) return null

  // 1) Decode once. Double-encoding will survive one pass and be caught below.
  const decoded = safeDecode(value.trim())
  if (decoded === null) return null

  // 2) Reject if the decoded value looks like it was still encoded.
  //    Double-encoding yields e.g. "%252F" which after one decode becomes "%2F".
  if (/%[0-9a-fA-F]{2}/.test(decoded)) return null

  // 3) Reject empty, no leading slash, double slash, backslash.
  if (!decoded.startsWith('/') || decoded.startsWith('//')) return null
  if (decoded.includes('\\')) return null

  // 4) Reject protocol-like prefixes (javascript:, data:, http:, https:, etc.).
  const lower = decoded.toLowerCase()
  if (/^[a-z][a-z0-9+.-]*:/.test(lower)) return null

  // 5) Strip trailing slash for allowlist comparison, but preserve query params.
  const qs = decoded.indexOf('?')
  const pathOnly = qs === -1 ? decoded : decoded.slice(0, qs)

  // 6) Check against explicit allowlist.
  if (!ALLOWED_REDIRECT_ROUTES.has(pathOnly)) return null

  return decoded
}
