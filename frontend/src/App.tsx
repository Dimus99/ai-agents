import { useEffect, useMemo, useState } from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { api } from './lib/api'
import { AgentList } from './components/AgentList'
import { AgentDetails } from './components/AgentDetails'
import Stats from './pages/Stats'
import Dashboard from './pages/Dashboard'

export default function App() {
  const [running, setRunning] = useState(false)

  const runAll = async () => {
    setRunning(true)
    try {
      await api.runAllAgents()
    } finally {
      setRunning(false)
    }
  }

  const evolve = async () => {
    await api.evolve()
  }

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between p-4">
          <Link to="/" className="font-semibold">AI Agents Orchestrator</Link>
          <div className="flex gap-2">
            <button onClick={runAll} className="px-3 py-1 bg-indigo-600 text-white rounded disabled:opacity-50" disabled={running}>
              Запустить всех агентов
            </button>
            <button onClick={evolve} className="px-3 py-1 bg-emerald-600 text-white rounded">
              Сформировать новое поколение
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-4">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/agents/:id" element={<AgentDetails />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </main>
    </div>
  )
}


