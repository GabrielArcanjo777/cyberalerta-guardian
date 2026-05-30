"use client"
import React, {useState} from 'react'
import {postRecovery} from '@/lib/api'
import Card from '@/components/Card'
import Button from '@/components/Button'

export default function Recovery(){
  const [state,setState]=useState({paid:false,clicked_link:false,shared_documents:false,shared_password:false,installed_app:false,shared_sms_code:false})
  const [result,setResult]=useState<any>(null)
  const [loading,setLoading]=useState(false)

  const labels = {
    paid: '\ud83d\udcb5 Fiz transfer\u00eancia/Pix',
    clicked_link: '\ud83d\udd17 Cliquei no link',
    shared_documents: '\ud83d\udcc4 Compartilhei documentos',
    shared_password: '\ud83d\udd10 Compartilhei senha',
    installed_app: '\ud83d\udcf1 Instalei app remoto',
    shared_sms_code: '\ud83d\udcb2 Passei c\u00f3digo SMS'
  }

  async function onSubmit(){
    setLoading(true)
    const res = await postRecovery(state)
    setResult(res)
    setLoading(false)
  };

  return (
    <main>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Já caí em um golpe?</h1>
        <p className="text-gray-600 mt-2">Receba um plano de ação para se recuperar</p>
      </div>

      <Card className="mb-6">
        <h2 className="text-lg font-semibold mb-4">Quais ações você fez?</h2>
        <div className="space-y-3 mb-6">
          {Object.entries(state).map(([k, v])=> (
            <label key={k} className="flex items-center gap-3 cursor-pointer p-2 hover:bg-gray-50 rounded">
              <input 
                type="checkbox" 
                checked={v} 
                onChange={e=>setState({...state, [k]: e.target.checked})}
                className="w-5 h-5 cursor-pointer"
              />
              <span className="font-medium text-gray-700">{labels[k as keyof typeof labels]}</span>
            </label>
          ))}
        </div>
        <Button onClick={onSubmit} disabled={loading}>
          {loading ? '⏳ Gerando checklist...' : '📋 Gerar meu plano de recuperação'}
        </Button>
      </Card>

      {result && (
        <>
          {result.__mock && (
            <Card className="mb-4 bg-blue-50">
              <p className="text-sm text-blue-800">ℹ️ Dados em modo demonstração</p>
            </Card>
          )}
          <Card>
            <h2 className="text-lg font-semibold mb-4">Seu plano de recuperação</h2>
            <div className="space-y-4">
              {result.checklist && result.checklist.map((item: string, i: number) => (
                <div key={i} className="flex items-start gap-3">
                  <div className="flex-shrink-0 flex items-center justify-center h-6 w-6 rounded-full bg-green-100">
                    <span className="text-green-700 font-bold text-sm">{i+1}</span>
                  </div>
                  <div>
                    <p className="text-gray-800">{item}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
              <p className="text-sm text-yellow-800"><strong>⚠️ Importante:</strong> Se voc\u00ea transferiu dinheiro, entre em contato imediatamente com seu banco!</p>
            </div>
          </Card>
        </>
      )}
    </main>
  )
}
