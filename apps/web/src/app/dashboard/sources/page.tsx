'use client'
import { useEffect, useState } from 'react'
import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'
import { getSources, deleteSource } from '@/lib/api/endpoints'
import { useSession } from 'next-auth/react'

interface Source {
  id: number
  program_id: number
  source_type: string
  source_url: string | null
  file_name: string | null
  status: string
  created_at: string
}

const STATUS_COLOR: Record<string, string> = {
  pending:    '#6b7a9e',
  processing: '#4d7cfe',
  completed:  '#29d987',
  failed:     '#f87171',
}

export default function SourcesPage() {
  const [sources, setSources]         = useState<Source[]>([])
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState('')
  const [statusFilter, setStatusFilter]   = useState('')
  const [programFilter, setProgramFilter] = useState('')
  const { status } = useSession()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const params: { status?: string; program_id?: number } = {}
      if (statusFilter)  params.status = statusFilter
      if (programFilter) params.program_id = Number(programFilter)
      const data = await getSources(params)
      setSources(data)
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load sources')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (status !== 'authenticated') {
      setLoading(status === 'loading')
      return
    }

    load()
  }, [status, statusFilter, programFilter])

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this source and all its chunks?')) return
    try {
      await deleteSource(id)
      setSources(s => s.filter(src => src.id !== id))
    } catch (e: any) {
      alert(e?.message ?? 'Delete failed')
    }
  }

  const label = (s: Source) =>
    s.source_url
      ? s.source_url.replace(/^https?:\/\//, '').slice(0, 60)
      : s.file_name ?? `Source #${s.id}`

  return (
    <div className="flex min-h-screen" style={{ background: '#0d1117' }}>
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-5xl mx-auto">

            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>Data Sources</h1>
                <p style={{ color: '#6b7a9e', fontSize: 14 }}>
                  Manage the documents and links indexed for curriculum comparison.
                </p>
              </div>
              <a href="/dashboard/ingest">
                <button
                  className="px-4 py-2 rounded-lg text-[14px] font-medium text-white"
                  style={{ background: '#4d7cfe' }}
                >
                  + Add Sources
                </button>
              </a>
            </div>

            {/* Filters */}
            <div className="flex gap-3 mb-6">
              <select
                value={statusFilter}
                onChange={e => setStatusFilter(e.target.value)}
                className="rounded-lg px-3 py-2 text-[13px] outline-none"
                style={{ background: '#111520', border: '1px solid #1e2740', color: '#6b7a9e' }}
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="processed">Processed</option>
                <option value="failed">Failed</option>
              </select>
              <input
                value={programFilter}
                onChange={e => setProgramFilter(e.target.value)}
                placeholder="Filter by program ID…"
                className="rounded-lg px-3 py-2 text-[13px] outline-none w-52"
                style={{ background: '#111520', border: '1px solid #1e2740', color: '#6b7a9e' }}
              />
              <button
                onClick={load}
                className="px-3 py-2 rounded-lg text-[13px]"
                style={{ background: '#111520', border: '1px solid #1e2740', color: '#6b7a9e' }}
              >
                ↻ Refresh
              </button>
            </div>

            {error && (
              <div className="rounded-lg px-4 py-3 mb-4 text-[13px]"
                   style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
                {error}
              </div>
            )}

            <div className="rounded-xl overflow-hidden" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              {/* Header row */}
              <div
                className="grid gap-4 px-6 py-3 text-[11px] font-semibold tracking-widest uppercase"
                style={{ color: '#6b7a9e', borderBottom: '1px solid #1e2740', gridTemplateColumns: '2fr 1fr 1fr 1fr auto' }}
              >
                <span>Source</span>
                <span>Type</span>
                <span>Program</span>
                <span>Status</span>
                <span></span>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-16" style={{ color: '#3d4d6e' }}>
                  <span className="text-[13px]">Loading…</span>
                </div>
              ) : sources.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16" style={{ color: '#3d4d6e' }}>
                  <span style={{ fontSize: 36, marginBottom: 12 }}>📂</span>
                  <p className="text-[14px]">No sources yet</p>
                  <p className="text-[12px] mt-1">Sources will appear here once ingested</p>
                </div>
              ) : (
                sources.map((s, i) => (
                  <div
                    key={s.id}
                    className="grid items-center gap-4 px-6 py-4 hover:bg-white/[0.02] transition-colors"
                    style={{
                      gridTemplateColumns: '2fr 1fr 1fr 1fr auto',
                      borderBottom: i < sources.length - 1 ? '1px solid #1a2035' : 'none',
                    }}
                  >
                    <span className="text-[13px] truncate" style={{ color: '#e8edf8' }} title={label(s)}>
                      {label(s)}
                    </span>
                    <span
                      className="text-[11px] font-semibold px-2 py-1 rounded w-fit"
                      style={{ background: 'rgba(77,124,254,0.1)', color: '#4d7cfe', border: '1px solid rgba(77,124,254,0.2)' }}
                    >
                      {s.source_type}
                    </span>
                    <span className="text-[13px]" style={{ color: '#6b7a9e' }}>#{s.program_id}</span>
                    <span
                      className="text-[11px] font-semibold px-2 py-1 rounded w-fit"
                      style={{ color: STATUS_COLOR[s.status] ?? '#6b7a9e', background: 'rgba(255,255,255,0.05)' }}
                    >
                      {s.status}
                    </span>
                    <button
                      onClick={() => handleDelete(s.id)}
                      className="text-white/20 hover:text-red-400 transition-colors text-[13px]"
                    >
                      🗑
                    </button>
                  </div>
                ))
              )}
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
