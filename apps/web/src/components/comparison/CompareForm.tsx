'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { apiClient, ApiError } from '@/lib/api/client'

// ─── Types ────────────────────────────────────────────────────────────────────

interface UniCardState {
  name: string
  sources: string[]
}

// ─── UniCard ──────────────────────────────────────────────────────────────────

function UniCard({
  label,
  color,
  defaultName,
  onChange,
}: {
  label: string
  color: 'blue' | 'gold'
  defaultName: string
  onChange: (state: UniCardState) => void
}) {
  const [name, setName] = useState(defaultName)
  const [sources, setSources] = useState<string[]>(
    defaultName === 'New York University'
      ? ['https://cs.nyu.edu/home/undergrad/cs_bs_program.html']
      : []
  )
  const [inputVal, setInputVal] = useState('')

  const borderColor = color === 'blue' ? '#4d7cfe' : '#f5a623'
  const bgColor     = color === 'blue' ? 'rgba(77,124,254,0.15)' : 'rgba(245,166,35,0.15)'
  const textColor   = color === 'blue' ? '#4d7cfe' : '#f5a623'

  const update = (nextName: string, nextSources: string[]) => {
    onChange({ name: nextName, sources: nextSources })
  }

  const handleNameChange = (val: string) => {
    setName(val)
    update(val, sources)
  }

  const addSource = () => {
    const trimmed = inputVal.trim()
    if (!trimmed) return
    const next = [...sources, trimmed]
    setSources(next)
    setInputVal('')
    update(name, next)
  }

  const removeSource = (idx: number) => {
    const next = sources.filter((_, i) => i !== idx)
    setSources(next)
    update(name, next)
  }

  return (
    <div className="flex-1 rounded-xl border border-white/10 bg-white/5 p-6">
      {/* University name row */}
      <div className="flex items-center gap-3 mb-4">
        <span
          className="flex items-center justify-center w-7 h-7 rounded-lg text-sm font-bold flex-shrink-0"
          style={{ background: bgColor, color: textColor }}
        >
          {label}
        </span>
        <input
          value={name}
          onChange={e => handleNameChange(e.target.value)}
          placeholder="University name..."
          className="flex-1 bg-transparent border-none outline-none text-white text-[15px] font-medium placeholder-white/30"
        />
      </div>

      {/* Sources label */}
      <p className="text-[11px] font-semibold tracking-widest text-white/30 uppercase mb-3">
        Sources ({sources.length} / 20)
      </p>

      {/* Existing sources */}
      {sources.map((s, i) => (
        <div
          key={i}
          className="flex items-center gap-2 rounded-lg px-3 py-2 mb-2"
          style={{ background: 'rgba(77,124,254,0.06)', border: '1px solid rgba(77,124,254,0.2)' }}
        >
          <span className="text-[#4d7cfe] text-xs">🔗</span>
          <span className="flex-1 text-white/60 text-[12px] truncate">{s}</span>
          <span
            className="text-[10px] font-bold px-2 py-0.5 rounded"
            style={{ background: 'rgba(77,124,254,0.2)', color: '#4d7cfe' }}
          >
            URL
          </span>
          <button
            onClick={() => removeSource(i)}
            className="text-white/20 hover:text-white/60 transition-colors text-lg leading-none ml-1"
          >
            ×
          </button>
        </div>
      ))}

      {/* Add source input */}
      <div className="flex items-center gap-2 rounded-lg px-3 py-2 mb-3 border border-dashed border-white/15">
        <span className="text-white/30">⊕</span>
        <input
          value={inputVal}
          onChange={e => setInputVal(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addSource()}
          placeholder="Paste a URL and press Enter..."
          className="flex-1 bg-transparent border-none outline-none text-white/60 text-[13px] placeholder-white/25"
        />
        <button
          onClick={addSource}
          className="text-[12px] px-2 py-1 rounded text-white/40 hover:text-white/70 transition-colors"
        >
          Add
        </button>
      </div>

      {/* Buttons */}
      <div className="flex gap-2">
        <button className="px-3 py-1.5 rounded-lg text-[13px] text-white/70 border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
          📎 Upload PDF
        </button>
        <button className="px-3 py-1.5 rounded-lg text-[13px] text-white/70 border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
          📋 Paste Text
        </button>
      </div>
    </div>
  )
}

// ─── CompareForm ──────────────────────────────────────────────────────────────

export default function CompareForm() {
  const router = useRouter()

  const [uniA, setUniA] = useState<UniCardState>({
    name: 'New York University',
    sources: ['https://cs.nyu.edu/home/undergrad/cs_bs_program.html'],
  })
  const [uniB, setUniB] = useState<UniCardState>({
    name: 'Carnegie Mellon University',
    sources: [],
  })

  const [programType, setProgramType] = useState('B.S. Computer Science')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleRun = async () => {
    setError('')

    if (!uniA.name.trim() || !uniB.name.trim()) {
      setError('Please enter names for both universities.')
      return
    }
    if (uniA.sources.length === 0 && uniB.sources.length === 0) {
      setError('Please add at least one source URL for either university.')
      return
    }

    setIsSubmitting(true)

    try {
      // 1. Create program records for both universities
      const [progA, progB] = await Promise.all([
        apiClient('/api/v1/programs/', {
          method: 'POST',
          body: JSON.stringify({ name: programType, institution: uniA.name }),
        }),
        apiClient('/api/v1/programs/', {
          method: 'POST',
          body: JSON.stringify({ name: programType, institution: uniB.name }),
        }),
      ])

      // 2. Create the comparison record
      const comparison = await apiClient('/api/v1/comparisons/', {
        method: 'POST',
        body: JSON.stringify({
          title: `${uniA.name} vs ${uniB.name} — ${programType}`,
          program_a_id: progA.id,
          program_b_id: progB.id,
        }),
      })

      // 3. Ingest sources for both programs (must await — comparison engine needs the chunks)
      const ingestPromises: Promise<unknown>[] = []

      if (uniA.sources.length > 0) {
        const formA = new FormData()
        formA.append('program_id', String(progA.id))
        formA.append('links', uniA.sources.join(','))
        ingestPromises.push(
          apiClient('/api/v1/ingest/', { method: 'POST', body: formA, headers: {} }).catch(() => null)
        )
      }

      if (uniB.sources.length > 0) {
        const formB = new FormData()
        formB.append('program_id', String(progB.id))
        formB.append('links', uniB.sources.join(','))
        ingestPromises.push(
          apiClient('/api/v1/ingest/', { method: 'POST', body: formB, headers: {} }).catch(() => null)
        )
      }

      await Promise.all(ingestPromises)

      // 4. Run the LLM comparison engine
      await apiClient(`/api/v1/comparisons/${comparison.id}/run`, { method: 'POST' })

      // 5. Navigate to results
      router.push(`/dashboard/results?id=${comparison.id}`)

    } catch (e) {
      if (e instanceof ApiError) {
        setError(e.message)
      } else {
        setError('Something went wrong. Please try again.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">New Comparison</h1>

      {/* University cards */}
      <div className="flex gap-4 mb-4">
        <UniCard label="A" color="blue" defaultName="New York University"        onChange={setUniA} />
        <UniCard label="B" color="gold" defaultName="Carnegie Mellon University" onChange={setUniB} />
      </div>

      {/* Options */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 mb-6">
        <h2 className="text-[15px] font-semibold text-white mb-4">Comparison Options</h2>
        <div className="grid grid-cols-3 gap-4">
          {/* Program type — this drives what gets sent to the API */}
          <div>
            <label className="block text-[11px] font-semibold tracking-widest text-white/30 uppercase mb-2">
              Program Type
            </label>
            <select
              value={programType}
              onChange={e => setProgramType(e.target.value)}
              className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white/80 text-[14px] outline-none cursor-pointer"
            >
              {['B.S. Computer Science', 'B.S. Electrical Engineering', 'M.S. Computer Science'].map(o => (
                <option key={o} className="bg-gray-900">{o}</option>
              ))}
            </select>
          </div>

          {/* Focus areas — UI only for now, passed later when LLM service exists */}
          <div>
            <label className="block text-[11px] font-semibold tracking-widest text-white/30 uppercase mb-2">
              Focus Areas
            </label>
            <select className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white/80 text-[14px] outline-none cursor-pointer">
              {['All', 'Core Requirements', 'Elective Structure', 'Specialization Tracks'].map(o => (
                <option key={o} className="bg-gray-900">{o}</option>
              ))}
            </select>
          </div>

          {/* Rigor metrics — UI only for now */}
          <div>
            <label className="block text-[11px] font-semibold tracking-widest text-white/30 uppercase mb-2">
              Rigor Metrics
            </label>
            <select className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white/80 text-[14px] outline-none cursor-pointer">
              {['Full Analysis', 'Quick Overview', 'Credit Hours Only'].map(o => (
                <option key={o} className="bg-gray-900">{o}</option>
              ))}
            </select>
          </div>
        </div>
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

      {/* Run row */}
      <div className="flex justify-end gap-3">
        <button className="px-6 py-2.5 rounded-lg text-[14px] text-white/70 border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
          Save as Draft
        </button>
        <button
          onClick={handleRun}
          disabled={isSubmitting}
          className="px-6 py-2.5 rounded-lg text-[15px] font-medium text-white transition-all hover:-translate-y-0.5 disabled:opacity-50 disabled:translate-y-0"
          style={{ background: '#4d7cfe' }}
        >
          {isSubmitting ? 'Ingesting & Analyzing…' : 'Run Comparison →'}
        </button>
      </div>
    </div>
  )
}