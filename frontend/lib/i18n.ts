export const supportedLocales = ['pt-BR', 'en-US'] as const

export type Locale = typeof supportedLocales[number]

export const defaultLocale:Locale = 'pt-BR'

export const messages = {
  'pt-BR': {
    tagline: 'Antes do Pix. Antes do clique. Antes do prejuízo.',
    protectivePause: 'O Guardian cria uma pausa protetiva antes de decisões digitais perigosas.',
    submitSuspiciousMessage: 'Enviar mensagem suspeita',
    trustLockActivated: 'Trust Lock ativado',
    familyConsole: 'Family Console',
    recoveryMode: 'Recovery Mode',
    trustCenter: 'Trust Center',
    impactDashboard: 'Impact Dashboard',
    pilotReadiness: 'Pilot Readiness',
    beforePix: 'Antes do Pix',
    integrations: 'Integrações',
    simulator: 'Simulador',
    globalApplicability: 'Global Applicability',
    helpNetwork: 'Rede de Ajuda',
  },
  'en-US': {
    tagline: 'Before payments. Before clicks. Before loss.',
    protectivePause: 'Guardian creates a protective pause before dangerous digital decisions.',
    submitSuspiciousMessage: 'Submit suspicious message',
    trustLockActivated: 'Trust Lock activated',
    familyConsole: 'Family Console',
    recoveryMode: 'Recovery Mode',
    trustCenter: 'Trust Center',
    impactDashboard: 'Impact Dashboard',
    pilotReadiness: 'Pilot Readiness',
    beforePix: 'Before action',
    integrations: 'Integrations',
    simulator: 'Simulator',
    globalApplicability: 'Global Applicability',
    helpNetwork: 'Help Network',
  },
} satisfies Record<Locale, Record<string, string>>

export function getMessages(locale:Locale){
  return messages[locale] || messages[defaultLocale]
}
