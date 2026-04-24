// TODO: plug in IngestForm component when ready
import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'

export default function IngestPage() {
  return (
    <div className="flex min-h-screen" style={{ background: '#0d1117' }}>
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-3xl mx-auto">

            {/* Page title */}
            <div className="mb-8">
              <h1 className="text-2xl font-bold mb-1" style={{ color: '#e8edf8' }}>
                Data Ingest
              </h1>
              <p style={{ color: '#6b7a9e', fontSize: 14 }}>
                Add URLs or PDFs to be processed and indexed as curriculum sources.
              </p>
            </div>

            {/* TODO: URL input section */}
            <div className="rounded-xl p-6 mb-4" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <h2 className="text-[13px] font-semibold tracking-widest uppercase mb-4" style={{ color: '#6b7a9e' }}>
                Add a Link
              </h2>
              <div className="flex gap-3">
                <input
                  type="url"
                  disabled
                  placeholder="https://university.edu/program/requirements"
                  className="flex-1 rounded-lg px-4 py-2.5 text-[14px] outline-none opacity-50"
                  style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid #1e2740', color: '#e8edf8' }}
                />
                <button
                  disabled
                  className="px-5 py-2.5 rounded-lg text-[14px] font-medium text-white opacity-40"
                  style={{ background: '#4d7cfe' }}
                >
                  Add URL
                </button>
              </div>
            </div>

            {/* TODO: PDF upload section */}
            <div className="rounded-xl p-6 mb-6" style={{ background: '#111520', border: '1px solid #1e2740' }}>
              <h2 className="text-[13px] font-semibold tracking-widest uppercase mb-4" style={{ color: '#6b7a9e' }}>
                Upload PDFs
              </h2>
              <div
                className="flex flex-col items-center justify-center gap-2 rounded-xl py-10"
                style={{ border: '2px dashed #1e2740' }}
              >
                <span style={{ fontSize: 28 }}>📄</span>
                <span style={{ color: '#6b7a9e', fontSize: 14 }}>
                  Drag & drop PDFs here, or <span style={{ color: '#4d7cfe' }}>browse</span>
                </span>
                <span style={{ color: '#3d4d6e', fontSize: 12 }}>
                  Syllabus PDFs, course handbooks, degree requirement sheets
                </span>
              </div>
            </div>

            {/* TODO: Entry queue list goes here */}
            <div
              className="rounded-xl p-6 mb-6 flex items-center justify-center"
              style={{ background: '#111520', border: '1px solid #1e2740', minHeight: 80 }}
            >
              <span style={{ color: '#3d4d6e', fontSize: 13 }}>Queue will appear here</span>
            </div>

            {/* Submit */}
            <div className="flex justify-end">
              <button
                disabled
                className="px-6 py-2.5 rounded-lg text-[15px] font-medium text-white opacity-40"
                style={{ background: '#4d7cfe' }}
              >
                Ingest Sources →
              </button>
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}