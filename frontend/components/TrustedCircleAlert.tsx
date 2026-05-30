import React from 'react'
import Card from '@/components/Card'

export default function TrustedCircleAlert({alert}:{alert:{should_alert:boolean,contact_name:string,message:string}}){
  if(!alert.should_alert) return null
  return (
    <Card className="border-l-4 border-orange-500 bg-orange-50">
      <div className="font-semibold text-orange-700">\u26a0\ufe0f Alertar Círculo de Confiança</div>
      <div className="mt-2 text-sm text-gray-700">{alert.message}</div>
      <div className="mt-2 text-sm font-semibold text-orange-800">Contato: {alert.contact_name}</div>
    </Card>
  )
}
