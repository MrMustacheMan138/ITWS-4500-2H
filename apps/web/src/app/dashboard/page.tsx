'use client'
import { useEffect, useState } from 'react'
import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'
import { getComparisons, getSources, getPrograms } from '@/lib/api/endpoints'
import { useSession } from 'next-auth/react'

interface Comparison {
  id: number
  title: string
  program_a_id: number | null
  program_b_id: number | null
  comparison_results: string | null
  created_at: string
}

function parseVerdict(raw: string | null) {
  try {
    if (!raw) return { verdict: '—', scoreA: 0, scoreB: 0 }
    const r = JSON.parse(raw)
    return { verdict: r.verdict ?? '—', scoreA: r.score_a ?? 0, scoreB: r.score_b ?? 0 }
  } catch {
    return { verdict: '—', scoreA: 0, scoreB: 0 }
  }
}

function abbr(title: string) {
  const m = title.match(/^(.+?)\s+vs\s+(.+?)(?:\s+[—–-]|$)/i)
  return m ? { a: m[1].trim(), b: m[2].trim() } : { a: 'A', b: 'B' }
}

export default function Dashboard() {
  const [comparisons, setComparisons] = useState<Comparison[]>([])
  const [sourceCount, setSourceCount] = useState(0)
  const [programCount, setProgramCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const { status } = useSession()

  useEffect(() => {
    if (status !== 'authenticated') {
      setLoading(status === 'loading')
      return
    }

    Promise.all([
      getComparisons().catch(() => []),
      getSources().catch(() => []),
      getPrograms().catch(() => []),
    ]).then(([comps, sources, progs]) => {
      setComparisons(comps)
      setSourceCount(sources.length)
      setProgramCount(progs.length)
    }).finally(() => setLoading(false))
  }, [status])

  const gapsTotal = comparisons.reduce((sum, c) => {
    try { return sum + (JSON.parse(c.comparison_results ?? '{}').gaps?.length ?? 0) }
    catch { return sum }
  }, 0)

  const stats = [
    { label: 'Comparisons Run',  value: loading ? '…' : String(comparisons.length), icon: '▦' },
    { label: 'Sources Analyzed', value: loading ? '…' : String(sourceCount),         icon: '📂' },
    { label: 'Programs',         value: loading ? '…' : String(programCount),         icon: '🏛' },
    { label: 'Gaps Identified',  value: loading ? '…' : String(gapsTotal),            icon: '◈' },
  ]

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-5xl mx-auto">

            <div className="mb-8">
              <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>Welcome back 👋</h1>
              <p style={{ color: '#6b7a9e', fontSize: 14 }}>Here's an overview of your curriculum comparisons.</p>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-4 gap-4 mb-8">
              {stats.map(s => (
                <div key={s.label} className="rounded-xl p-5" style={{ background: '#111520', border: '1px solid #1e2740' }}>
                  <div className="text-2xl mb-2">{s.icon}</div>
                  <div className="text-[28px] font-bold mb-1" style={{ color: '#e8edf8' }}>{s.value}</div>
                  <div className="text-[12px]" style={{ color: '#6b7a9e' }}>{s.label}</div>
                </div>
              ))}
            </div>

            {/* Recent comparisons */}
            <div className="rounded-xl overflow-hidden" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid #1e2740' }}>
                <h2 className="text-[15px] font-semibold" style={{ color: '#e8edf8' }}>Recent Comparisons</h2>
                <a href="/dashboard/compare/new">
                  <button className="px-4 py-1.5 rounded-lg text-[13px] font-medium text-white" style={{ background: '#4d7cfe' }}>
                    + New Comparison
                  </button>
                </a>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-12" style={{ color: '#3d4d6e' }}>
                  <span className="text-[13px]">Loading…</span>
                </div>
              ) : comparisons.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12" style={{ color: '#3d4d6e' }}>
                  <span style={{ fontSize: 28, marginBottom: 8 }}>▦</span>
                  <p className="text-[13px]">No comparisons yet — start one above</p>
                </div>
              ) : (
                comparisons.map((c, i) => {
                  const { a, b } = abbr(c.title)
                  const { verdict, scoreA, scoreB } = parseVerdict(c.comparison_results)
                  return (
                    <div
                      key={c.id}
                      className="flex items-center px-6 py-4 hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                      style={{ borderBottom: i < comparisons.length - 1 ? '1px solid #1e2740' : 'none' }}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[15px] font-bold" style={{ color: '#4d7cfe' }}>{a}</span>
                          <span style={{ color: '#3d4d6e' }}>vs</span>
                          <span className="text-[15px] font-bold" style={{ color: '#f5a623' }}>{b}</span>
                        </div>
                        <div className="text-[12px]" style={{ color: '#6b7a9e' }}>
                          {c.title} · {new Date(c.created_at).toLocaleDateString()}
                        </div>
                      </div>

                      <div className="flex items-center gap-6 mr-6">
                        <div className="text-center">
                          <div className="text-[20px] font-bold" style={{ color: '#4d7cfe' }}>{scoreA || '—'}</div>
                          <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{a.slice(0, 6)}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-[20px] font-bold" style={{ color: '#f5a623' }}>{scoreB || '—'}</div>
                          <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{b.slice(0, 6)}</div>
                        </div>
                      </div>

                      <div className="mr-6">
                        <span className="px-3 py-1 rounded-full text-[11px] font-semibold"
                              style={{ background: 'rgba(77,124,254,0.1)', color: '#6b8fff', border: '1px solid rgba(77,124,254,0.2)' }}>
                          {verdict}
                        </span>
                      </div>

                      <a href={`/dashboard/results?id=${c.id}`}>
                        <button className="px-3 py-1.5 rounded-lg text-[12px] transition-colors"
                                style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #1e2740', color: '#6b7a9e' }}>
                          View →
                        </button>
                      </a>
                    </div>
                  )
                })
              )}
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
