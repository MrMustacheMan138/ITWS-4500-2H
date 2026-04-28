'use client'
import { useEffect, useState, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'
import { useSession } from 'next-auth/react'
import { getComparisons } from '@/lib/api/endpoints'
import Link from 'next/link'

// ─── Types ────────────────────────────────────────────────────────────────────

interface SectionScore {
  section_id: string
  score: number       // Program A score
  score_b: number     // Program B score
  strengths: string[]
  weaknesses: string[]
}

interface ComparisonResults {
  score_a: number
  score_b: number
  verdict: string
  section_scores: SectionScore[]
  gaps: { title: string; body: string; cite?: string }[]
}

interface Comparison {
  id: number
  title: string
  program_a_id: number | null
  program_b_id: number | null
  comparison_results: string | null
  created_at?: string
}

interface Program {
  id: number
  name: string
  institution: string | null
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function parseResults(raw: string | null): ComparisonResults | null {
  if (!raw) return null
  try {
    return JSON.parse(raw) as ComparisonResults
  } catch {
    return null
  }
}

function abbr(title: string) {
  const m = title.match(/^(.+?)\s+vs\s+(.+?)(?:\s+[—–-]|$)/i)
  if (m) return { a: m[1].trim(), b: m[2].trim() }
  const dash = title.indexOf('—')
  if (dash > 0) return { a: title.slice(0, dash).trim(), b: '?' }
  return { a: title.slice(0, 20), b: '?' }
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function PendingBadge({ label }: { label: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-center">
      <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">{label}</p>
      <p className="text-[28px] font-bold leading-none mb-2 text-white/20">—</p>
      <p className="text-white/20 text-[12px]">Pending analysis</p>
    </div>
  )
}

function ScoreCard({ label, score, color }: { label: string; score: number; color: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-center">
      <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">{label}</p>
      <p className="text-[52px] font-bold leading-none mb-2" style={{ color }}>{score}</p>
      <p className="text-white/40 text-[12px]">out of 100</p>
    </div>
  )
}

// ─── Comparison List View (when no ?id= in URL) ──────────────────────────────

function ComparisonList() {
  const [comparisons, setComparisons] = useState<Comparison[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const { status } = useSession()

  useEffect(() => {
  if (status !== 'authenticated') return
  getComparisons()
    .then(setComparisons)
    .catch(e => setError(e instanceof ApiError ? e.message : 'Failed to load comparisons.'))
    .finally(() => setIsLoading(false))
  }, [status])

  if (isLoading || status === 'loading') {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 animate-pulse h-40" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto">
        <div
          className="rounded-lg px-4 py-3 text-[13px]"
          style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}
        >
          {error}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>Comparison Results</h1>
        <p style={{ color: '#6b7a9e', fontSize: 14 }}>Browse all of your past curriculum comparisons.</p>
      </div>

      <div className="rounded-xl overflow-hidden" style={{ background: '#111520', border: '1px solid #1e2740' }}>
        <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: '1px solid #1e2740' }}>
          <h2 className="text-[15px] font-semibold" style={{ color: '#e8edf8' }}>
            All Comparisons {comparisons.length > 0 && (
              <span className="text-[12px] font-normal" style={{ color: '#6b7a9e' }}>· {comparisons.length}</span>
            )}
          </h2>
          <Link href="/dashboard/compare/new">
            <button className="px-4 py-1.5 rounded-lg text-[13px] font-medium text-white" style={{ background: '#4d7cfe' }}>
              + New Comparison
            </button>
          </Link>
        </div>

        {comparisons.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16" style={{ color: '#3d4d6e' }}>
            <span style={{ fontSize: 32, marginBottom: 8 }}>▦</span>
            <p className="text-[13px] mb-3">No comparisons yet</p>
            <Link href="/dashboard/compare/new">
              <button className="px-4 py-2 rounded-lg text-[13px] font-medium text-white" style={{ background: '#4d7cfe' }}>
                Start Your First Comparison
              </button>
            </Link>
          </div>
        ) : (
          comparisons.map((c, i) => {
            const { a, b } = abbr(c.title)
            const parsed = parseResults(c.comparison_results)
            return (
              <Link
                key={c.id}
                href={`/dashboard/results?id=${c.id}`}
                className="flex items-center px-6 py-4 hover:bg-[rgba(255,255,255,0.02)] transition-colors no-underline"
                style={{ borderBottom: i < comparisons.length - 1 ? '1px solid #1e2740' : 'none' }}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[15px] font-bold" style={{ color: '#4d7cfe' }}>{a}</span>
                    <span style={{ color: '#3d4d6e' }}>vs</span>
                    <span className="text-[15px] font-bold" style={{ color: '#f5a623' }}>{b}</span>
                  </div>
                  <div className="text-[12px]" style={{ color: '#6b7a9e' }}>
                    {c.title}
                    {c.created_at && ` · ${new Date(c.created_at).toLocaleDateString()}`}
                  </div>
                </div>

                <div className="flex items-center gap-6 mr-6">
                  <div className="text-center">
                    <div className="text-[20px] font-bold" style={{ color: '#4d7cfe' }}>
                      {parsed?.score_a ?? '—'}
                    </div>
                    <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{a.slice(0, 6)}</div>
                  </div>
                  <div className="text-center">
                    <div className="text-[20px] font-bold" style={{ color: '#f5a623' }}>
                      {parsed?.score_b ?? '—'}
                    </div>
                    <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{b.slice(0, 6)}</div>
                  </div>
                </div>

                <span
                  className="px-3 py-1.5 rounded-lg text-[12px]"
                  style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #1e2740', color: '#6b7a9e' }}
                >
                  View →
                </span>
              </Link>
            )
          })
        )}
      </div>
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function ResultsView() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const comparisonId = searchParams.get('id')
  const { status } = useSession()
  const resultsRef = useRef<HTMLDivElement>(null)
  
  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [programA, setProgramA] = useState<Program | null>(null)
  const [programB, setProgramB] = useState<Program | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const handleExportPdf = async () => {
  if (!resultsRef.current) return
  const html2pdf = (await import('html2pdf.js')).default
  html2pdf()
    .set({
      margin: 0.5,
      filename: `${comparison?.title ?? 'comparison'}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, backgroundColor: '#0d1117' },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
    })
    .from(resultsRef.current)
    .save()
  }


  useEffect(() => {
    // If no id in URL, skip the detail load — list view will fetch its own data
    if (!comparisonId) {
      setIsLoading(false)
      return
    }

    if (status !== 'authenticated') return

    const load = async () => {
      try {
        const comp: Comparison = await apiClient(`/api/v1/comparisons/${comparisonId}`)
        setComparison(comp)

        const [pA, pB] = await Promise.all([
          comp.program_a_id ? apiClient(`/api/v1/programs/${comp.program_a_id}`) : null,
          comp.program_b_id ? apiClient(`/api/v1/programs/${comp.program_b_id}`) : null,
        ])
        setProgramA(pA)
        setProgramB(pB)
      } catch (e) {
        setError(e instanceof ApiError ? e.message : 'Failed to load comparison.')
      } finally {
        setIsLoading(false)
      }
    }

    load()
  }, [comparisonId, status])

  // ── No id in URL → show list of all comparisons ────────────────────────────
  if (!comparisonId) {
    return <ComparisonList />
  }

  // ── Loading detail ─────────────────────────────────────────────────────────
  if (isLoading || status === 'loading') {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 mb-5 animate-pulse">
          <div className="h-6 rounded w-48 mb-2" style={{ background: '#1e2740' }} />
          <div className="h-3 rounded w-64" style={{ background: '#1e2740' }} />
        </div>
        <div className="grid grid-cols-3 gap-4 mb-5">
          {[0, 1, 2].map(i => (
            <div key={i} className="rounded-xl border border-white/10 bg-white/5 p-6 h-36 animate-pulse" style={{ background: '#111520' }} />
          ))}
        </div>
      </div>
    )
  }

  // ── Error ──────────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="max-w-5xl mx-auto">
        <div className="rounded-lg px-4 py-3 text-[13px]" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}>
          {error}
        </div>
      </div>
    )
  }

  // ── Comparison not found ───────────────────────────────────────────────────
  if (!comparison) {
    return (
      <div className="max-w-5xl mx-auto flex flex-col items-center justify-center py-24" style={{ color: '#3d4d6e' }}>
        <span style={{ fontSize: 36, marginBottom: 12 }}>▦</span>
        <p className="text-[14px]">Comparison not found</p>
        <button
          onClick={() => router.push('/dashboard/results')}
          className="mt-4 px-4 py-2 rounded-lg text-[13px] font-medium text-white"
          style={{ background: '#4d7cfe' }}
        >
          Back to All Comparisons
        </button>
      </div>
    )
  }

  const results = parseResults(comparison.comparison_results)
  const nameA = programA?.institution ?? programA?.name ?? 'University A'
  const nameB = programB?.institution ?? programB?.name ?? 'University B'
  const shortA = nameA.split(' ').map((w: string) => w[0]).join('').slice(0, 4)
  const shortB = nameB.split(' ').map((w: string) => w[0]).join('').slice(0, 4)

  return (
    <div className="max-w-5xl mx-auto">

      {/* Header */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 mb-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-[22px] font-bold mb-1">
              <span style={{ color: '#4d7cfe' }}>{nameA}</span>
              <span className="text-white/20 mx-2">vs</span>
              <span style={{ color: '#f5a623' }}>{nameB}</span>
            </div>
            <p className="text-white/40 text-[12px]">
              {comparison.title}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push('/dashboard/results')}
              className="px-3 py-1.5 rounded-lg text-[13px] border border-white/10 transition-colors hover:bg-white/10"
              style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)' }}
            >
              ← All Results
            </button>
            <button
              onClick={handleExportPdf}
              className="px-3 py-1.5 rounded-lg text-[13px] border border-white/10 transition-colors hover:bg-white/10"
              style={{ background: 'rgba(255,255,255,0.05)', color: 'rgba(255,255,255,0.7)' }}
            >
              ↓ Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* Score cards */}
      <div className="grid grid-cols-3 gap-4 mb-5">
        {results ? (
          <>
            <ScoreCard label={`${nameA} Rigor Score`} score={results.score_a} color="#4d7cfe" />
            <div className="rounded-xl p-6 text-center" style={{ background: 'rgba(77,124,254,0.08)', border: '1px solid rgba(77,124,254,0.3)' }}>
              <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">Overall Verdict</p>
              <p className="text-[18px] font-bold text-white mb-1">{results.verdict}</p>
              <p className="text-white/40 text-[12px]">
                {results.section_scores?.length
                  ? `across ${results.section_scores.length} sections`
                  : 'Full analysis complete'}
              </p>
            </div>
            <ScoreCard label={`${nameB} Rigor Score`} score={results.score_b} color="#f5a623" />
          </>
        ) : (
          <>
            <PendingBadge label={`${nameA} Rigor Score`} />
            <div className="rounded-xl p-6 text-center" style={{ background: 'rgba(77,124,254,0.08)', border: '1px solid rgba(77,124,254,0.3)' }}>
              <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">Overall Verdict</p>
              <p className="text-[18px] font-bold text-white/30 mb-1">Awaiting analysis</p>
              <p className="text-white/20 text-[12px]">LLM scoring in progress</p>
            </div>
            <PendingBadge label={`${nameB} Rigor Score`} />
          </>
        )}
      </div>

      {/* Section scores table — only when results exist */}
      {results?.section_scores?.length ? (
        <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden mb-5">
          <div className="grid grid-cols-4 px-6 py-3 border-b border-white/10 text-[11px] font-semibold tracking-widest uppercase text-white/30">
            <div>Section</div>
            <div>{shortA} Score</div>
            <div>{shortB} Score</div>
            <div>Δ Difference</div>
          </div>
          {results.section_scores.map((row, i) => {
            const aScore = row.score ?? 0
            const bScore = (row as any).score_b ?? 0
            const delta = aScore - bScore
            const winner = delta >= 0 ? 'a' : 'b'
            return (
              <div
                key={row.section_id}
                className="grid grid-cols-4 px-6 py-4 items-center hover:bg-white/5 transition-colors"
                style={{ borderBottom: i < results.section_scores.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none' }}
              >
                <div className="text-white/90 text-[14px] font-medium capitalize">
                  {row.section_id.replace(/_/g, ' ')}
                </div>
                <div className="text-[13px]" style={{ color: '#4d7cfe' }}>{aScore}</div>
                <div className="text-[13px]" style={{ color: '#f5a623' }}>{bScore}</div>
                <div>
                  <span
                    className="inline-block px-2.5 py-1 rounded-md text-[11px] font-semibold"
                    style={{
                      background: winner === 'b' ? 'rgba(245,166,35,0.12)' : 'rgba(77,124,254,0.12)',
                      color: winner === 'b' ? '#f5a623' : '#6b8fff',
                      border: `1px solid ${winner === 'b' ? 'rgba(245,166,35,0.2)' : 'rgba(77,124,254,0.2)'}`,
                    }}
                  >
                    {delta === 0 ? 'Tied' : winner === 'b' ? `B +${Math.abs(delta)}` : `A +${Math.abs(delta)}`}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden mb-5">
          <div className="grid grid-cols-4 px-6 py-3 border-b border-white/10 text-[11px] font-semibold tracking-widest uppercase text-white/30">
            <div>Section</div><div>{shortA}</div><div>{shortB}</div><div>Δ Difference</div>
          </div>
          <div className="flex flex-col items-center justify-center py-12" style={{ color: '#3d4d6e' }}>
            <span style={{ fontSize: 28, marginBottom: 8 }}>⏳</span>
            <p className="text-[13px]">Section scores will appear once analysis is complete</p>
          </div>
        </div>
      )}

      {/* AI Gap Analysis */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-[15px] font-semibold text-white">AI Gap Analysis</h3>
          {results?.gaps?.length ? (
            <span
              className="text-[11px] font-bold px-2.5 py-1 rounded-full"
              style={{ background: 'rgba(255,77,106,0.15)', color: '#ff4d6a', border: '1px solid rgba(255,77,106,0.25)' }}
            >
              {results.gaps.length} gap{results.gaps.length !== 1 ? 's' : ''} identified
            </span>
          ) : null}
        </div>
        <p className="text-[11px] text-white/30 mb-4">◆ All claims linked to source documents</p>

        {results?.gaps?.length ? (
          results.gaps.map(g => (
            <div
              key={g.title}
              className="rounded-lg p-4 mb-3 last:mb-0"
              style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}
            >
              <p className="font-semibold text-white text-[13.5px] mb-1">{g.title}</p>
              <p className="text-white/50 text-[12.5px] mb-2">{g.body}</p>
              {g.cite && (
                <p className="text-[11px] cursor-pointer hover:underline" style={{ color: '#4d7cfe' }}>
                  📎 {g.cite}
                </p>
              )}
            </div>
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-8" style={{ color: '#3d4d6e' }}>
            <span style={{ fontSize: 28, marginBottom: 8 }}>◈</span>
            <p className="text-[13px]">Gap analysis will appear once the LLM scores the programs</p>
          </div>
        )}

        <div className="mt-4">
          <button
            onClick={() => router.push(`/dashboard/chat?id=${comparisonId}`)}
            className="px-4 py-2 rounded-lg text-[13px] font-medium text-white transition-all hover:-translate-y-0.5"
            style={{ background: '#4d7cfe' }}
          >
            Ask AI about these gaps →
          </button>
        </div>
      </div>

    </div>
  )
}