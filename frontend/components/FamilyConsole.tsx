import React from 'react'

export default function FamilyConsole({contact,summary}:{contact:string,summary:string}){
  return (
    <div className="p-4 bg-white border rounded">
      <div className="font-semibold">Family Console - {contact}</div>
      <div className="mt-2 text-sm">{summary}</div>
      <div className="mt-3">
        <button className="px-4 py-2 bg-black text-white rounded">Ligue agora</button>
      </div>
    </div>
  )
}
