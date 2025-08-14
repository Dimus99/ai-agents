import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import Stats from './Stats'
import { RecentRuns } from '../components/RecentRuns'

export default function Dashboard() {
  const [status, setStatus] = useState<any>(null)
  useEffect(() => { api.status().then(setStatus) }, [])
  return (
    <div className="space-y-4">
      <div className="bg-white border rounded p-3">
        <div className="text-sm text-gray-500 mb-1">Статус</div>
        {status?.running ? (
          <div className="text-emerald-700">Идёт раунд: {status.round.name} (#{status.round.id})</div>
        ) : (
          <div className="text-gray-700">Сейчас раунд не идёт</div>
        )}
      </div>
      <Stats />
      <RecentRuns />
    </div>
  )
}


