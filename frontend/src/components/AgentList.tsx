import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, Agent } from '../lib/api'

export function AgentList() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [type, setType] = useState<string>('all')
  const [generation, setGeneration] = useState<string>('all')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    api.listAgents().then((data) => setAgents(data)).finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    return agents.filter(a => (type === 'all' || a.agent_type === type) && (generation === 'all' || a.generation === Number(generation)))
  }, [agents, type, generation])

  return (
    <div className="space-y-4">
      <div className="flex gap-3 items-end">
        <div>
          <label className="block text-sm">Тип</label>
          <select className="border rounded px-2 py-1" value={type} onChange={e=>setType(e.target.value)}>
            <option value="all">Все</option>
            <option value="technical">Тех.анализ</option>
            <option value="news">Новости</option>
          </select>
        </div>
        <div>
          <label className="block text-sm">Поколение</label>
          <input className="border rounded px-2 py-1 w-24" placeholder="all" value={generation} onChange={e=>setGeneration(e.target.value || 'all')} />
        </div>
      </div>

      {loading && <div>Загрузка...</div>}
      {!loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filtered.map((a) => (
            <div key={a.id} className="bg-white rounded border p-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{a.name}</div>
                  <div className="text-xs text-gray-500">{a.agent_type} • gen {a.generation}</div>
                </div>
                <Link to={`/agents/${a.id}`} className="text-indigo-600">Детали</Link>
              </div>
              <div className="mt-2 text-sm line-clamp-3 whitespace-pre-wrap">{a.prompt}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


