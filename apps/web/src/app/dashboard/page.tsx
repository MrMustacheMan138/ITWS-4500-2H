import Header from "@/components/common/header"
import Sidebar from "@/components/common/sidebar"

const recentComparisons = [
  { a: 'NYU', b: 'CMU',      program: 'B.S. Computer Science', date: 'Mar 11, 2026', verdict: 'CMU more rigorous',  scoreA: 74, scoreB: 87 },
  { a: 'MIT', b: 'Stanford', program: 'B.S. Computer Science', date: 'Mar 9, 2026',  verdict: 'MIT more rigorous',  scoreA: 91, scoreB: 88 },
  { a: 'RPI', b: 'RIT',      program: 'B.S. Computer Science', date: 'Mar 7, 2026',  verdict: 'RPI more rigorous',  scoreA: 79, scoreB: 73 },
]

const stats = [
  { label: 'Comparisons Run',   value: '12', icon: '▦' },
  { label: 'Sources Analyzed',  value: '48', icon: '📂' },
  { label: 'Universities',      value: '8',  icon: '🏛' },
  { label: 'Gaps Identified',   value: '31', icon: '◈' },
]

export default function Dashboard() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <div className="max-w-5xl mx-auto">

            {/* Welcome */}
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

              {recentComparisons.map((c, i) => (
                <div
                  key={i}
                  className="flex items-center px-6 py-4 transition-colors cursor-pointer"
                  style={{ borderBottom: i < recentComparisons.length - 1 ? '1px solid #1e2740' : 'none' }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.02)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'transparent')}
                >
                  {/* Unis */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[15px] font-bold" style={{ color: '#4d7cfe' }}>{c.a}</span>
                      <span style={{ color: '#3d4d6e' }}>vs</span>
                      <span className="text-[15px] font-bold" style={{ color: '#f5a623' }}>{c.b}</span>
                    </div>
                    <div className="text-[12px]" style={{ color: '#6b7a9e' }}>{c.program} · {c.date}</div>
                  </div>

                  {/* Scores */}
                  <div className="flex items-center gap-6 mr-6">
                    <div className="text-center">
                      <div className="text-[20px] font-bold" style={{ color: '#4d7cfe' }}>{c.scoreA}</div>
                      <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{c.a}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-[20px] font-bold" style={{ color: '#f5a623' }}>{c.scoreB}</div>
                      <div className="text-[10px]" style={{ color: '#6b7a9e' }}>{c.b}</div>
                    </div>
                  </div>

                  {/* Verdict */}
                  <div className="mr-6">
                    <span className="px-3 py-1 rounded-full text-[11px] font-semibold" style={{ background: 'rgba(77,124,254,0.1)', color: '#6b8fff', border: '1px solid rgba(77,124,254,0.2)' }}>
                      {c.verdict}
                    </span>
                  </div>

                  {/* Arrow */}
                  <a href="/dashboard/results">
                    <button className="px-3 py-1.5 rounded-lg text-[12px] transition-colors" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #1e2740', color: '#6b7a9e' }}>
                      View →
                    </button>
                  </a>
                </div>
              ))}
            </div>

          </div>
        </main>
      </div>
    </div>
  )
}