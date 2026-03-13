'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

function UniCard({ label, color, defaultName }: { label: string; color: 'blue' | 'gold'; defaultName: string }) {
  const [sources, setSources] = useState<string[]>(
    defaultName === 'New York University'
      ? ['https://cs.nyu.edu/home/undergrad/cs_bs_program.html']
      : []
  )
  const [inputVal, setInputVal] = useState('')

  const addSource = () => {
    if (inputVal.trim()) {
      setSources(prev => [...prev, inputVal.trim()])
      setInputVal('')
    }
  }

  const borderColor = color === 'blue' ? '#4d7cfe' : '#f5a623'
  const bgColor = color === 'blue' ? 'rgba(77,124,254,0.15)' : 'rgba(245,166,35,0.15)'
  const textColor = color === 'blue' ? '#4d7cfe' : '#f5a623'

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
          defaultValue={defaultName}
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
          <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: 'rgba(77,124,254,0.2)', color: '#4d7cfe' }}>URL</span>
        </div>
      ))}

      {/* Add source input */}
      <div className="flex items-center gap-2 rounded-lg px-3 py-2 mb-3 border border-dashed border-white/15">
        <span className="text-white/30">⊕</span>
        <input
          value={inputVal}
          onChange={e => setInputVal(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && addSource()}
          placeholder="Paste a URL, upload a PDF, or type/paste text..."
          className="flex-1 bg-transparent border-none outline-none text-white/60 text-[13px] placeholder-white/25"
        />
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

export default function CompareForm() {
  const router = useRouter()

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold text-white mb-6">New Comparison</h1>

      {/* University cards */}
      <div className="flex gap-4 mb-4">
        <UniCard label="A" color="blue" defaultName="New York University" />
        <UniCard label="B" color="gold" defaultName="Carnegie Mellon University" />
      </div>

      {/* Options */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 mb-6">
        <h2 className="text-[15px] font-semibold text-white mb-4">Comparison Options</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'PROGRAM TYPE',  options: ['B.S. Computer Science', 'B.S. Electrical Engineering', 'M.S. Computer Science'] },
            { label: 'FOCUS AREAS',   options: ['All', 'Core Requirements', 'Elective Structure', 'Specialization Tracks'] },
            { label: 'RIGOR METRICS', options: ['Full Analysis', 'Quick Overview', 'Credit Hours Only'] },
          ].map(f => (
            <div key={f.label}>
              <label className="block text-[11px] font-semibold tracking-widest text-white/30 uppercase mb-2">{f.label}</label>
              <select className="w-full bg-black/30 border border-white/10 rounded-lg px-3 py-2.5 text-white/80 text-[14px] outline-none cursor-pointer">
                {f.options.map(o => <option key={o} className="bg-gray-900">{o}</option>)}
              </select>
            </div>
          ))}
        </div>
      </div>

      {/* Run row */}
      <div className="flex justify-end gap-3">
        <button className="px-6 py-2.5 rounded-lg text-[14px] text-white/70 border border-white/10 bg-white/5 hover:bg-white/10 transition-colors">
          Save as Draft
        </button>
        <button
          onClick={() => router.push('/dashboard/results')}
          className="px-6 py-2.5 rounded-lg text-[15px] font-medium text-white transition-all hover:-translate-y-0.5"
          style={{ background: '#4d7cfe' }}
        >
          Run Comparison →
        </button>
      </div>
    </div>
  )
}
