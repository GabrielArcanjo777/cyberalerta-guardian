import React from 'react'
import Card from '@/components/Card'

export default function TrustLockCard({activated,reason,message}:{activated:boolean,reason:string,message:string}){
  return (
    <Card className={activated ? 'border-l-4 border-red-500 bg-red-50' : ''}>
      <div className={`font-bold text-lg ${activated ? 'text-red-700' : 'text-gray-700'}`}>
        {activated ? '🔒 TRUST LOCK ATIVADO' : 'Trust Lock'}
      </div>
      <div className="text-sm text-gray-600 mt-2">{reason}</div>
      <div className="mt-3 font-semibold text-gray-800">{message}</div>
    </Card>
  )
}
