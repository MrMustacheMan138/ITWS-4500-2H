'use client'
import { useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'

const MAX_SOURCES = 5

// ─── Types ────────────────────────────────────────────────────────────────────

interface SourceEntry {
  kind: 'url' | 'pdf'
  label: string       // display name: the URL string or the filename
  file?: File         // only set when kind === 'pdf'
}

interface UniCardState {
  name: string
  institution: string
  sources: SourceEntry[]
}

// ─── UniCard ──────────────────────────────────────────────────────────────────

function UniCard({
  label,
  color,
  state,
  onChange,
}: {
  label: string
  color: 'blue' | 'gold'
  state: UniCardState
  onChange: (s: UniCardState) => void
}) {
  const [urlInput, setUrlInput] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const accent   = color === 'blue' ? '#4d7cfe' : '#f5a623'
  const accentBg = color === 'blue' ? 'rgba(77,124,254,0.12)' : 'rgba(245,166,35,0.12)'
  const accentBorder = color === 'blue' ? 'rgba(77,124,254,0.25)' : 'rgba(245,166,35,0.25)'

  const remaining = MAX_SOURCES - state.sources.length

  const addUrl = () => {
    const trimmed = urlInput.trim()
    if (!trimmed || remaining <= 0) return
    onChange({ ...state, sources: [...state.sources, { kind: 'url', label: trimmed }] })
    setUrlInput('')
  }

  const addFiles = (files: FileList | null) => {
    if (!files) return
    const pdfs = Array.from(files).filter(f => f.name.toLowerCase().endsWith('.pdf'))
    const slots = Math.min(pdfs.length, remaining)
    const entries: SourceEntry[] = pdfs.slice(0, slots).map(f => ({
      kind: 'pdf',
      label: f.name,
      file: f,
    }))
    onChange({ ...state, sources: [...state.sources, ...entries] })
  }

  const remove = (idx: number) => {
    onChange({ ...state, sources: state.sources.filter((_, i) => i !== idx) })
  }

  return (
    <div
      className="flex-1 rounded-xl p-6 flex flex-col gap-4"
      style={{ background: '#111520', border: `1px solid ${accentBorder}` }}
    >
      {/* Header badge */}
      <div className="flex items-center gap-3">
        <span
          className="w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold flex-shrink-0"
          style={{ background: accentBg, color: accent }}
        >
          {label}
        </span>
        <span className="text-[13px] font-semibold tracking-widest uppercase" style={{ color: accent }}>
          Program {label}
        </span>
      </div>

      {/* University name */}
      <div>
        <label className="block text-[11px] font-semibold tracking-widest uppercase mb-1.5" style={{ color: '#6b7a9e' }}>
          University
        </label>
        <input
          value={state.name}
          onChange={e => onChange({ ...state, name: e.target.value })}
          placeholder="e.g. New York University"
          className="w-full rounded-lg px-3 py-2.5 text-[14px] outline-none"
          style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
        />
      </div>

      {/* Institution / Department */}
      <div>
        <label className="block text-[11px] font-semibold tracking-widest uppercase mb-1.5" style={{ color: '#6b7a9e' }}>
          Department / Program Name
        </label>
        <input
          value={state.institution}
          onChange={e => onChange({ ...state, institution: e.target.value })}
          placeholder="e.g. B.S. Computer Science"
          className="w-full rounded-lg px-3 py-2.5 text-[14px] outline-none"
          style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
        />
      </div>

      {/* Sources section */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="text-[11px] font-semibold tracking-widest uppercase" style={{ color: '#6b7a9e' }}>
            Sources
          </label>
          <span className="text-[11px]" style={{ color: remaining === 0 ? '#f87171' : '#3d4d6e' }}>
            {state.sources.length} / {MAX_SOURCES}
          </span>
        </div>

        {/* Existing sources */}
        <div className="flex flex-col gap-1.5 mb-3">
          {state.sources.map((s, i) => (
            <div
              key={i}
              className="flex items-center gap-2 rounded-lg px-3 py-2"
              style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid #1e2740' }}
            >
              <span className="text-xs">{s.kind === 'url' ? '🔗' : '📄'}</span>
              <span className="flex-1 text-[12px] truncate" style={{ color: '#e8edf8' }} title={s.label}>
                {s.label}
              </span>
              <span
                className="text-[10px] font-bold px-1.5 py-0.5 rounded flex-shrink-0"
                style={{ background: accentBg, color: accent }}
              >
                {s.kind.toUpperCase()}
              </span>
              <button
                onClick={() => remove(i)}
                className="text-white/20 hover:text-white/60 text-base leading-none ml-1 flex-shrink-0"
              >
                ×
              </button>
            </div>
          ))}

          {state.sources.length === 0 && (
            <p className="text-[12px] py-2" style={{ color: '#3d4d6e' }}>
              No sources added yet.
            </p>
          )}
        </div>

        {/* URL input */}
        {remaining > 0 && (
          <div className="flex gap-2 mb-2">
            <input
              type="url"
              value={urlInput}
              onChange={e => setUrlInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addUrl()}
              placeholder="Paste a URL…"
              className="flex-1 rounded-lg px-3 py-2 text-[13px] outline-none"
              style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
            />
            <button
              onClick={addUrl}
              className="px-3 py-2 rounded-lg text-[13px] font-medium text-white flex-shrink-0"
              style={{ background: accent }}
            >
              Add
            </button>
          </div>
        )}

        {/* PDF upload button */}
        {remaining > 0 ? (
          <button
            onClick={() => fileRef.current?.click()}
            className="w-full rounded-lg py-2 text-[13px] border border-dashed transition-colors"
            style={{ borderColor: '#1e2740', color: '#6b7a9e' }}
          >
            📄 Upload PDF{remaining > 1 ? 's' : ''} ({remaining} slot{remaining !== 1 ? 's' : ''} left)
          </button>
        ) : (
          <p className="text-center text-[12px] py-1" style={{ color: '#f87171' }}>
            Source limit reached
          </p>
        )}

        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={e => addFiles(e.target.files)}
        />
      </div>
    </div>
  )
}

// Progress overlay shown during the multi-step submission 

function ProgressOverlay({ step }: { step: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(13,17,23,0.85)' }}>
      <div className="rounded-2xl p-10 flex flex-col items-center gap-4" style={{ background: '#111520', border: '1px solid #1e2740' }}>
        <div className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin" style={{ borderColor: '#4d7cfe', borderTopColor: 'transparent' }} />
        <p className="text-[14px] font-medium" style={{ color: '#e8edf8' }}>{step}</p>
      </div>
    </div>
  )
}

// CompareForm 

export default function CompareForm() {
  const router = useRouter()

  const [sideA, setSideA] = useState<UniCardState>({ name: '', institution: '', sources: [] })
  const [sideB, setSideB] = useState<UniCardState>({ name: '', institution: '', sources: [] })
  const [progressStep, setProgressStep] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleRun = async () => {
    setError('')

    // Validation 
    if (!sideA.name.trim() || !sideB.name.trim()) {
      setError('Please enter a university name for both programs.')
      return
    }
    if (sideA.sources.length === 0 || sideB.sources.length === 0) {
      setError('Please add at least one source for each program.')
      return
    }

    setIsSubmitting(true)

    try {
      // 1. Create both programs 
      setProgressStep('Creating program records…')
      const [progA, progB] = await Promise.all([
        apiClient('/api/v1/programs/', {
          method: 'POST',
          body: JSON.stringify({ name: sideA.institution || sideA.name, institution: sideA.name }),
        }),
        apiClient('/api/v1/programs/', {
          method: 'POST',
          body: JSON.stringify({ name: sideB.institution || sideB.name, institution: sideB.name }),
        }),
      ])

      // 2. Create the comparison record 
      setProgressStep('Setting up comparison…')
      const compTitle = `${sideA.name} vs ${sideB.name}${sideA.institution ? ` — ${sideA.institution}` : ''}`
      const comparison = await apiClient('/api/v1/comparisons/', {
        method: 'POST',
        body: JSON.stringify({ title: compTitle, program_a_id: progA.id, program_b_id: progB.id }),
      })

      // 3. Ingest sources for both programs 
      // Each side sends its own FormData with its own mix of URLs and files.
      setProgressStep('Ingesting sources for both programs…')

      const buildForm = (programId: number, state: UniCardState): FormData => {
        const form = new FormData()
        form.append('program_id', String(programId))
        const urls = state.sources.filter(s => s.kind === 'url').map(s => s.label)
        if (urls.length > 0) form.append('links', urls.join(','))
        state.sources.filter(s => s.kind === 'pdf' && s.file).forEach(s => form.append('files', s.file!))
        return form
      }

      await Promise.all([
        apiClient('/api/v1/ingest/', { method: 'POST', body: buildForm(progA.id, sideA), headers: {} }),
        apiClient('/api/v1/ingest/', { method: 'POST', body: buildForm(progB.id, sideB), headers: {} }),
      ])

      // 4. Run the LLM comparison engine
      setProgressStep('Running AI comparison… (this may take ~20 seconds)')
      await apiClient(`/api/v1/comparisons/${comparison.id}/run`, { method: 'POST' })

      // 5. Navigate to results 
      router.push(`/dashboard/results?id=${comparison.id}`)

    } catch (e) {
      setError(e instanceof ApiError ? e.message : 'Something went wrong. Please try again.')
      setIsSubmitting(false)
      setProgressStep('')
    }
  }

  return (
    <>
      {isSubmitting && <ProgressOverlay step={progressStep} />}

      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>New Comparison</h1>
          <p style={{ color: '#6b7a9e', fontSize: 14 }}>
            Add up to {MAX_SOURCES} sources per program — any mix of URLs and PDFs.
          </p>
        </div>

        {/* Side-by-side cards */}
        <div className="flex gap-4 mb-6">
          <UniCard label="A" color="blue" state={sideA} onChange={setSideA} />
          <UniCard label="B" color="gold" state={sideB} onChange={setSideB} />
        </div>

        {/* Error */}
        {error && (
          <div
            className="rounded-lg px-4 py-3 mb-4 text-[13px]"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171' }}
          >
            {error}
          </div>
        )}

        {/* Submit row */}
        <div className="flex justify-end">
          <button
            onClick={handleRun}
            disabled={isSubmitting}
            className="px-8 py-3 rounded-lg text-[15px] font-medium text-white disabled:opacity-40"
            style={{ background: '#4d7cfe' }}
          >
            Run Comparison →
          </button>
        </div>
      </div>
    </>
  )
}