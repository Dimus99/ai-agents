import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Stats() {
  const [stats, setStats] = useState<any>(null)
  useEffect(() => { api.stats().then(setStats) }, [])
  if (!stats) return <div>Загрузка...</div>
  const data = stats.pnl_by_generation.map((d: any) => ({ generation: d.generation, pnl: d.total_pnl }))
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white border rounded p-3">Всего агентов: {stats.total_agents}</div>
        <div className="bg-white border rounded p-3">Активных: {stats.active_agents}</div>
        <div className="bg-white border rounded p-3">Раундов: {stats.total_rounds}</div>
        <div className="bg-white border rounded p-3">Запусков: {stats.total_runs}</div>
      </div>
      <div className="bg-white border rounded p-3">
        <div className="text-sm text-gray-500 mb-2">PnL по поколениям</div>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="generation" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="pnl" stroke="#6366f1" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}


