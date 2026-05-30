import React from 'react'
import Card from '@/components/Card'

export default function RiskScore({score,level}:{score:number,level:string}){
  const color = level === 'critical' ? 'text-red-700 bg-red-50' : level === 'high' ? 'text-yellow-700 bg-yellow-50' : 'text-green-700 bg-green-50'
  const borderColor = level === 'critical' ? 'border-l-4 border-red-500' : level === 'high' ? 'border-l-4 border-yellow-500' : 'border-l-4 border-green-500'
  return (
    <Card className={`${borderColor} ${color}`}>
      <div className="text-center">
        <div className="text-4xl font-bold">{score}</div>
        <div className="text-sm font-semibold mt-1 uppercase tracking-wide">{level}</div>
      </div>
    </Card>
  )
}
