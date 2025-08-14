import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api, Agent, AgentRun } from '../lib/api'

export function AgentDetails() {
  const { id } = useParams()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [runs, setRuns] = useState<AgentRun[]>([])
  const [loading, setLoading] = useState(false)
  const agentId = Number(id)

  useEffect(() => {
    if (!agentId) return
    setLoading(true)
    Promise.all([api.getAgent(agentId), api.getAgentRuns(agentId)])
      .then(([a, r]) => { setAgent(a); setRuns(r) })
      .finally(() => setLoading(false))
  }, [agentId])

  const runNow = async () => {
    await api.runAgent(agentId)
    const r = await api.getAgentRuns(agentId)
    setRuns(r)
  }

  if (!agent) return <div>Загрузка...</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">{agent.name}</h1>
          <div className="text-sm text-gray-500">{agent.agent_type} • gen {agent.generation}</div>
        </div>
        <button onClick={runNow} className="px-3 py-1 bg-indigo-600 text-white rounded">Запустить агента</button>
      </div>
      <div className="bg-white border rounded p-3 whitespace-pre-wrap">
        <div className="text-sm text-gray-500 mb-1">Промпт</div>
        {agent.prompt}
      </div>
      <div className="bg-white border rounded p-3">
        <div className="text-sm text-gray-500 mb-2">Последние запуски</div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="py-1">Round</th>
              <th className="py-1">Signal</th>
              <th className="py-1">PnL</th>
              <th className="py-1">At</th>
            </tr>
          </thead>
          <tbody>
            {runs.map(r => (
              <tr key={r.id} className="border-t">
                <td className="py-1">{r.round_id}</td>
                <td className="py-1">{r.signal}</td>
                <td className="py-1">{r.pnl}</td>
                <td className="py-1">{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


