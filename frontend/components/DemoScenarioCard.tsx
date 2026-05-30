import React from 'react'
import Link from 'next/link'

export default function DemoScenarioCard({title,href}:{title:string,href:string}){
  return (
    <Link href={href} className="block p-4 bg-white border rounded hover:shadow">
      <h4 className="font-semibold">{title}</h4>
      <p className="text-sm text-gray-600 mt-1">Clique para abrir e testar o scenario.</p>
    </Link>
  )
}
