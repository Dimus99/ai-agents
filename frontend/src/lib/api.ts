import axios from 'axios'

export type Agent = {
  id: number
  name: string
  agent_type: 'technical' | 'news'
  generation: number
  prompt: string
  is_active: boolean
  created_at: string
}

export type AgentRun = {
  id: number
  agent_id: number
  round_id: number
  signal: 'buy' | 'sell' | 'hold' | null
  pnl: number
  details?: string | null
  created_at: string
}

const client = axios.create({ baseURL: import.meta.env.VITE_API_BASE || 'http://localhost:8000' })

export const api = {
  listAgents: async (): Promise<Agent[]> => {
    const { data } = await client.get('/agents')
    return data
  },
  getAgent: async (id: number): Promise<Agent> => {
    const { data } = await client.get(`/agents/${id}`)
    return data
  },
  getAgentRuns: async (id: number): Promise<AgentRun[]> => {
    const { data } = await client.get(`/api/agents/${id}/runs`) // internal route for runs
    return data
  },
  runAgent: async (id: number) => {
    await client.post(`/api/agents/${id}/run`)
  },
  runAllAgents: async () => {
    await client.post('/agents/run')
  },
  evolve: async () => {
    await client.post('/agents/evolve')
  },
  stats: async () => {
    const { data } = await client.get('/stats')
    return data
  },
  status: async () => {
    const { data } = await client.get('/status')
    return data
  },
  recentRuns: async (limit = 50) => {
    const { data } = await client.get('/recent-runs', { params: { limit } })
    return data as Array<{id:number; agent_id:number; agent_name:string; round_id:number; signal:string; pnl:number; created_at:string}>
  }
}


