// TODO: plug in SourcesTable component when ready
import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'

export default function SourcesPage() {
  return (
    <div className="flex min-h-screen" style={{ background: '#0d1117' }}>
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-5xl mx-auto">

            {/* Page title */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>
                  Data Sources
                </h1>
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

            {/* TODO: filter controls go here */}
            <div className="flex gap-3 mb-6">
              <select
                disabled
                className="rounded-lg px-3 py-2 text-[13px] outline-none opacity-50 cursor-not-allowed"
                style={{ background: '#111520', border: '1px solid #1e2740', color: '#6b7a9e' }}
              >
                <option>All Statuses</option>
              </select>
              <input
                disabled
                placeholder="Filter by program ID…"
                className="rounded-lg px-3 py-2 text-[13px] outline-none w-52 opacity-50"
                style={{ background: '#111520', border: '1px solid #1e2740', color: '#6b7a9e' }}
              />
            </div>

            {/* TODO: sources table goes here */}
            <div className="rounded-xl overflow-hidden" style={{ background: '#111520', border: '1px solid #1e2740' }}>

              {/* Column headers */}
              <div
                className="grid grid-cols-[2fr_1fr_1fr_1fr_auto] gap-4 px-6 py-3 text-[11px] font-semibold tracking-widest uppercase"
                style={{ color: '#6b7a9e', borderBottom: '1px solid #1e2740' }}
              >
                <span>Source</span>
                <span>Type</span>
                <span>Program</span>
                <span>Status</span>
                <span></span>
              </div>

              {/* Empty state placeholder */}
              <div className="flex flex-col items-center justify-center py-16" style={{ color: '#3d4d6e' }}>
                <span style={{ fontSize: 36, marginBottom: 12 }}>📂</span>
                <p className="text-[14px]">No sources yet</p>
                <p className="text-[12px] mt-1">Sources will appear here once ingested</p>
              </div>

            </div>

          </div>
        </main>
      </div>
    </div>
  )
}