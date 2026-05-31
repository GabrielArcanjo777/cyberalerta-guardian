import React from 'react'
import AssistedProtectionDemo from '@/components/AssistedProtectionDemo'
import {PageShell} from '@/components/CommandCenter'

export default function AssistedDemoPage(){
  return (
    <PageShell maxWidth="7xl" className="pb-16">
      <AssistedProtectionDemo />
    </PageShell>
  )
}
