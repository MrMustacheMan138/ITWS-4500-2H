'use client'
import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'

// ─── Types ────────────────────────────────────────────────────────────────────

interface SectionScore {
  section_id: string
  score: number
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
  comparison_results: string | null  // JSON string from the DB
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

// ─── Main Component ───────────────────────────────────────────────────────────

export default function ResultsView() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const comparisonId = searchParams.get('id')

  const [comparison, setComparison] = useState<Comparison | null>(null)
  const [programA, setProgramA] = useState<Program | null>(null)
  const [programB, setProgramB] = useState<Program | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!comparisonId) {
      setIsLoading(false)
      return
    }

    const load = async () => {
      try {
        // Fetch comparison
        const comp: Comparison = await apiClient(`/api/v1/comparisons/${comparisonId}`)
        setComparison(comp)

        // Fetch both programs in parallel if IDs exist
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
  }, [comparisonId])

  // ── Loading ────────────────────────────────────────────────────────────────
  if (isLoading) {
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

  // ── No ID in URL ───────────────────────────────────────────────────────────
  if (!comparisonId || !comparison) {
    return (
      <div className="max-w-5xl mx-auto flex flex-col items-center justify-center py-24" style={{ color: '#3d4d6e' }}>
        <span style={{ fontSize: 36, marginBottom: 12 }}>▦</span>
        <p className="text-[14px]">No comparison selected</p>
        <button
          onClick={() => router.push('/dashboard/compare/new')}
          className="mt-4 px-4 py-2 rounded-lg text-[13px] font-medium text-white"
          style={{ background: '#4d7cfe' }}
        >
          Start a New Comparison
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
            {['✏ Markup', '↓ Export PDF', '↗ Share'].map((label, i) => (
              <button
                key={label}
                className="px-3 py-1.5 rounded-lg text-[13px] border border-white/10 transition-colors hover:bg-white/10"
                style={{ background: i === 2 ? '#4d7cfe' : 'rgba(255,255,255,0.05)', color: i === 2 ? '#fff' : 'rgba(255,255,255,0.7)' }}
              >
                {label}
              </button>
            ))}
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
        /* Placeholder table when no results yet */
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
            onClick={() => router.push('/dashboard/chat')}
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