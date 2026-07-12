"use client"

import React from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import GuardianAdminConsole from '@/components/GuardianAdminConsole'
import {PageShell} from '@/components/CommandCenter'

export default function FamilyConsolePage(){
  return (
    <ProtectedRoute>
      {(user)=> (
        <PageShell maxWidth="7xl">
          <GuardianAdminConsole operatorName={user.full_name} />
        </PageShell>
      )}
    </ProtectedRoute>
  )
}
