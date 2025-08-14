import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export function RecentRuns() {
  const [rows, setRows] = useState<any[]>([])
  useEffect(() => {
    let mounted = true
    const load = async () => {
      const data = await api.recentRuns(50)
      if (mounted) setRows(data)
    }
    load()
    const id = setInterval(load, 5000)
    return () => { mounted = false; clearInterval(id) }
  }, [])

  return (
    <div className="bg-white border rounded p-3">
      <div className="text-sm text-gray-500 mb-2">Последние запуски</div>
      <div className="max-h-80 overflow-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th className="py-1">Agent</th>
              <th className="py-1">Round</th>
              <th className="py-1">Signal</th>
              <th className="py-1">PnL</th>
              <th className="py-1">At</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} className="border-t">
                <td className="py-1">{r.agent_name} ({r.agent_id})</td>
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


