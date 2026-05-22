import { useState, useEffect } from 'react'
import { Phone, PhoneOff, BarChart3, Activity, DollarSign, TrendingUp } from 'lucide-react'

const API = 'http://localhost:8000/api/v1'

export default function App() {
  const [tab, setTab] = useState<'dashboard'|'calls'|'agents'>('dashboard')
  const [dashboard, setDashboard] = useState<any>(null)
  const [calls, setCalls] = useState<any[]>([])
  const [agents, setAgents] = useState<any>(null)

  useEffect(() => {
    fetch(`${API}/dashboard`).then(r=>r.json()).then(setDashboard).catch(console.error)
    fetch(`${API}/calls`).then(r=>r.json()).then(d=>setCalls(d.calls)).catch(console.error)
    fetch(`${API}/agents/status`).then(r=>r.json()).then(setAgents).catch(console.error)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Intelligent Call Deflection</h1>
          <p className="text-sm text-gray-500">AI-powered call-to-digital deflection engine</p>
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-4 py-6">
        <nav className="flex space-x-1 mb-6 bg-white rounded-lg shadow p-1 border">
          {[{id:'dashboard' as const,label:'Dashboard',icon:BarChart3},{id:'calls' as const,label:'Call Log',icon:Phone},{id:'agents' as const,label:'Agents',icon:Activity}].map(t=>(
            <button key={t.id} onClick={()=>setTab(t.id)} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium ${tab===t.id?'bg-green-100 text-green-700':'text-gray-600 hover:bg-gray-100'}`}>
              <t.icon className="w-4 h-4"/>{t.label}
            </button>
          ))}
        </nav>

        {tab==='dashboard' && dashboard && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {[
                {label:'Total Calls',value:dashboard.total_calls,icon:Phone,color:'text-blue-600'},
                {label:'Deflection Rate',value:`${dashboard.deflection_rate}%`,icon:TrendingUp,color:'text-green-600'},
                {label:'Cost Saved',value:`$${dashboard.total_cost_saved.toLocaleString()}`,icon:DollarSign,color:'text-purple-600'},
                {label:'Avg Confidence',value:`${(dashboard.avg_confidence*100).toFixed(0)}%`,icon:Activity,color:'text-orange-600'},
              ].map(k=>(
                <div key={k.label} className="bg-white rounded-lg shadow p-4 border">
                  <div className="flex items-center justify-between">
                    <div><p className="text-sm text-gray-500">{k.label}</p><p className="text-2xl font-bold mt-1">{k.value}</p></div>
                    <k.icon className={`w-8 h-8 ${k.color}`}/>
                  </div>
                </div>
              ))}
            </div>
            <div className="bg-white rounded-lg shadow p-6 border">
              <h3 className="font-semibold mb-2">Cost Impact</h3>
              <p className="text-sm text-gray-600">Each deflected call saves ~$5.50 (avg call cost $7.00 vs digital $1.50)</p>
              <p className="text-3xl font-bold text-green-600 mt-2">${dashboard.total_cost_saved.toLocaleString()} saved</p>
            </div>
          </div>
        )}

        {tab==='calls' && (
          <div className="bg-white rounded-lg shadow border overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b"><tr>
                <th className="px-4 py-3 text-left">Call ID</th>
                <th className="px-4 py-3 text-left">Biller</th>
                <th className="px-4 py-3 text-left">Reason</th>
                <th className="px-4 py-3 text-center">Confidence</th>
                <th className="px-4 py-3 text-left">Channel</th>
                <th className="px-4 py-3 text-center">Outcome</th>
                <th className="px-4 py-3 text-right">Saved</th>
              </tr></thead>
              <tbody className="divide-y">
                {calls.slice(0,50).map(c=>(
                  <tr key={c.call_id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono text-xs">{c.call_id}</td>
                    <td className="px-4 py-3">{c.biller}</td>
                    <td className="px-4 py-3"><span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{c.reason?.replace('_',' ')}</span></td>
                    <td className="px-4 py-3 text-center font-mono">{c.confidence?.toFixed(2)}</td>
                    <td className="px-4 py-3 text-xs">{c.channel?.replace('_',' ')}</td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs ${c.outcome==='deflected'||c.outcome==='completed_digital'?'bg-green-100 text-green-700':'bg-gray-100 text-gray-600'}`}>{c.outcome?.replace('_',' ')}</span>
                    </td>
                    <td className="px-4 py-3 text-right text-green-600">{c.cost_saved>0?`$${c.cost_saved}`:'-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab==='agents' && agents && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {agents.agents.map((a:any)=>(
              <div key={a.name} className="bg-white rounded-lg shadow p-4 border">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">{a.name}</h4>
                  <span className="w-3 h-3 rounded-full bg-green-400"/>
                </div>
                <p className="text-sm text-gray-500">Status: {a.status}</p>
                <p className="text-sm text-gray-500">Processed: {a.records_processed}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
