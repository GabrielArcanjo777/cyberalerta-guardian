import React from 'react'
import Card from '@/components/Card'

export default function ReportCard({report}:{report:{title:string,summary:string,agent_decision:string,recommended_next_step:string}}){
  return (
    <Card>
      <div className="font-semibold text-lg">{report.title}</div>
      <div className="mt-3 space-y-3 text-sm">
        <div>
          <div className="font-semibold text-gray-800">Resumo</div>
          <p className="text-gray-700 mt-1">{report.summary}</p>
        </div>
        <div>
          <div className="font-semibold text-gray-800">Decisão</div>
          <p className="text-gray-700 mt-1">{report.agent_decision}</p>
        </div>
        <div>
          <div className="font-semibold text-gray-800">Próximos Passos</div>
          <p className="text-gray-700 mt-1">{report.recommended_next_step}</p>
        </div>
      </div>
    </Card>
  )
}
