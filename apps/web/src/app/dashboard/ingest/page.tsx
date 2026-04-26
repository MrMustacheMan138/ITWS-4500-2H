'use client'
import { useEffect, useRef, useState } from 'react'
import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'
import { getPrograms, ingestSources } from '@/lib/api/endpoints'
import { useSession } from 'next-auth/react'

interface Program {
  id: number
  name: string
  institution?: string
}

interface QueueEntry {
  id: string
  label: string
  type: 'url' | 'pdf'
  file?: File
  status: 'queued' | 'uploading' | 'done' | 'error'
  message?: string
}

const STATUS_COLOR: Record<string, string> = {
  queued:    '#6b7a9e',
  uploading: '#4d7cfe',
  done:      '#29d987',
  error:     '#f87171',
}

export default function IngestPage() {
  const [programs, setPrograms]       = useState<Program[]>([])
  const [programId, setProgramId]     = useState<number | null>(null)
  const [loadingProgs, setLoadingProgs] = useState(false)
  const [urlInput, setUrlInput]       = useState('')
  const [queue, setQueue]             = useState<QueueEntry[]>([])
  const [submitting, setSubmitting]   = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)
  const { status } = useSession()

  useEffect(() => {
    if (status !== 'authenticated') {
      setLoadingProgs(status === 'loading')
      return
    }

    setLoadingProgs(true)
    getPrograms()
      .then((data: Program[]) => {
        setPrograms(data)
        if (data.length > 0) setProgramId(data[0].id)
      })
      .catch(() => {})
      .finally(() => setLoadingProgs(false))
  }, [status])

  const addUrl = () => {
    const trimmed = urlInput.trim()
    if (!trimmed) return
    setQueue(q => [...q, { id: crypto.randomUUID(), label: trimmed, type: 'url', status: 'queued' }])
    setUrlInput('')
  }

  const addFiles = (files: FileList | null) => {
    if (!files) return
    const entries: QueueEntry[] = Array.from(files)
      .filter(f => f.name.toLowerCase().endsWith('.pdf'))
      .map(f => ({ id: crypto.randomUUID(), label: f.name, type: 'pdf', file: f, status: 'queued' as const }))
    setQueue(q => [...q, ...entries])
  }

  const removeEntry = (id: string) => setQueue(q => q.filter(e => e.id !== id))

  const patch = (id: string, update: Partial<QueueEntry>) =>
    setQueue(q => q.map(e => (e.id === id ? { ...e, ...update } : e)))

  const handleSubmit = async () => {
    if (!programId) { alert('Select a program first.'); return }
    const pending = queue.filter(e => e.status === 'queued')
    if (!pending.length) return

    const urls = pending.filter(e => e.type === 'url').map(e => e.label)
    const files = pending.filter(e => e.type === 'pdf' && e.file).map(e => e.file as File)

    setSubmitting(true)

    pending.forEach(entry => patch(entry.id, { status: 'uploading' }))

    try {
      const res = await ingestSources(programId, urls, files)
      pending.forEach(entry => patch(entry.id, { status: 'done', message: `${res.sources_processed ?? res.chunks_saved ?? 'Done'}` }))
    } catch (err: any) {
      pending.forEach(entry => patch(entry.id, { status: 'error', message: err?.message ?? 'Failed' }))
    }

    setSubmitting(false)
  }

  return (
    <div className="flex min-h-screen" style={{ background: '#0d1117' }}>
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-3xl mx-auto">

            <div className="mb-8">
              <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>Data Ingest</h1>
              <p style={{ color: '#6b7a9e', fontSize: 14 }}>
                Add URLs or PDFs to be processed and indexed as curriculum sources.
              </p>
            </div>

            {/* Program selector */}
            <div className="rounded-xl p-5 mb-4" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <label className="block text-[11px] font-semibold tracking-widest uppercase mb-2" style={{ color: '#6b7a9e' }}>
                Target Program
              </label>
              {loadingProgs ? (
                <p style={{ color: '#3d4d6e', fontSize: 13 }}>Loading programs…</p>
              ) : programs.length === 0 ? (
                <p style={{ color: '#f87171', fontSize: 13 }}>
                  No programs yet — run a comparison first to create programs.
                </p>
              ) : (
                <select
                  value={programId ?? ''}
                  onChange={e => setProgramId(Number(e.target.value))}
                  className="w-full rounded-lg px-3 py-2.5 text-[14px] outline-none"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
                >
                  {programs.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.institution ? `${p.institution} — ` : ''}{p.name}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* URL input */}
            <div className="rounded-xl p-6 mb-4" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <h2 className="text-[13px] font-semibold tracking-widest uppercase mb-4" style={{ color: '#6b7a9e' }}>
                Add a Link
              </h2>
              <div className="flex gap-3">
                <input
                  type="url"
                  value={urlInput}
                  onChange={e => setUrlInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && addUrl()}
                  placeholder="https://university.edu/program/requirements"
                  className="flex-1 rounded-lg px-4 py-2.5 text-[14px] outline-none"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
                />
                <button
                  onClick={addUrl}
                  className="px-5 py-2.5 rounded-lg text-[14px] font-medium text-white"
                  style={{ background: '#4d7cfe' }}
                >
                  Add URL
                </button>
              </div>
            </div>

            {/* PDF upload */}
            <div className="rounded-xl p-6 mb-6" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <h2 className="text-[13px] font-semibold tracking-widest uppercase mb-4" style={{ color: '#6b7a9e' }}>
                Upload PDFs
              </h2>
              <div
                className="flex flex-col items-center justify-center gap-2 rounded-xl py-10 cursor-pointer"
                style={{ border: '2px dashed #1e2740' }}
                onClick={() => fileRef.current?.click()}
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); addFiles(e.dataTransfer.files) }}
              >
                <span style={{ fontSize: 28 }}>📄</span>
                <span style={{ color: '#6b7a9e', fontSize: 14 }}>
                  Drag & drop PDFs here, or <span style={{ color: '#4d7cfe' }}>browse</span>
                </span>
                <span style={{ color: '#3d4d6e', fontSize: 12 }}>
                  Syllabus PDFs, course handbooks, degree requirement sheets
                </span>
              </div>
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                multiple
                className="hidden"
                onChange={e => addFiles(e.target.files)}
              />
            </div>

            {/* Queue */}
            <div className="rounded-xl p-6 mb-6" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <h2 className="text-[13px] font-semibold tracking-widest uppercase mb-4" style={{ color: '#6b7a9e' }}>
                Queue ({queue.length})
              </h2>
              {queue.length === 0 ? (
                <div className="flex items-center justify-center py-4">
                  <span style={{ color: '#3d4d6e', fontSize: 13 }}>Queue will appear here</span>
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {queue.map(entry => (
                    <div
                      key={entry.id}
                      className="flex items-center gap-3 rounded-lg px-4 py-2.5"
                      style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid #1e2740' }}
                    >
                      <span style={{ fontSize: 15 }}>{entry.type === 'url' ? '🔗' : '📄'}</span>
                      <span className="flex-1 text-[13px] truncate" style={{ color: '#e8edf8' }}>{entry.label}</span>
                      {entry.message && (
                        <span className="text-[11px]" style={{ color: STATUS_COLOR[entry.status] }}>{entry.message}</span>
                      )}
                      <span
                        className="text-[11px] font-semibold px-2 py-0.5 rounded"
                        style={{ color: STATUS_COLOR[entry.status], background: 'rgba(255,255,255,0.05)' }}
                      >
                        {entry.status}
                      </span>
                      {entry.status === 'queued' && (
                        <button
                          onClick={() => removeEntry(entry.id)}
                          className="text-white/20 hover:text-white/60 text-lg ml-1"
                        >×</button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit */}
            <div className="flex justify-end">
              <button
                onClick={handleSubmit}
                disabled={submitting || queue.filter(e => e.status === 'queued').length === 0}
                className="px-6 py-2.5 rounded-lg text-[15px] font-medium text-white disabled:opacity-40"
                style={{ background: '#4d7cfe' }}
              >
                {submitting ? 'Ingesting…' : 'Ingest Sources →'}
              </button>
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}
