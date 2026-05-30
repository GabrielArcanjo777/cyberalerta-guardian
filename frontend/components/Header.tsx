import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'

export default function Header(){
  return (
    <header className="flex items-center justify-between py-4 border-b border-gray-100">
      <div>
        <h3 className="text-xl font-bold">CyberAlerta Guardian</h3>
        <p className="text-sm text-gray-500">Antes do Pix. Antes do clique.</p>
      </div>
      <nav className="flex gap-3">
        <Link href="/before-pix"><Button variant="ghost">Antes do Pix</Button></Link>
        <Link href="/simulator"><Button variant="ghost">Simulador</Button></Link>
        <Link href="/recovery"><Button variant="ghost">Recovery</Button></Link>
      </nav>
    </header>
  )
}
