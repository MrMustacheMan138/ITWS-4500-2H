'use client'
import { useRouter } from 'next/navigation'

const tableData = [
  { category: 'Required Core Credits',         a: '64 credits · 16 courses',   b: '72 credits · 18 courses',      winner: 'b' },
  { category: 'Prerequisite Depth (avg chain)', a: '3.2 levels',                b: '4.1 levels',                   winner: 'b' },
  { category: 'Capstone / Senior Project',      a: 'Required · 6 credits',      b: 'Required · 9 credits',         winner: 'b' },
  { category: 'Elective Flexibility',           a: '28 credits free electives', b: '18 credits free electives',    winner: 'a' },
  { category: 'Specialization Tracks',          a: '4 tracks',                  b: '6 tracks',                     winner: 'b' },
  { category: 'Industry/Internship Credit',     a: 'Optional · up to 4 cr',     b: 'Not offered',                  winner: 'a' },
  { category: 'Theory Emphasis',                a: 'Moderate',                  b: 'High',                         winner: 'b' },
]

const gaps = [
  { title: 'Distributed Systems', body: 'CMU offers a structured 4-course track; NYU has no equivalent concentration.', cite: 'CMU SCS Catalog 2024, p. 34' },
  { title: 'Prerequisite Depth',  body: "CMU's algorithms sequence averages 3.8 prerequisite levels vs. NYU's 2.1.",    cite: 'NYU Bulletin 2024-25' },
]

export default function ResultsView() {
  const router = useRouter()

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6 mb-5">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-[22px] font-bold mb-1">
              <span style={{ color: '#4d7cfe' }}>NYU</span>
              <span className="text-white/20 mx-2">vs</span>
              <span style={{ color: '#f5a623' }}>CMU</span>
            </div>
            <p className="text-white/40 text-[12px]">B.S. Computer Science · Analyzed from 8 sources</p>
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
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-center">
          <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">NYU Rigor Score</p>
          <p className="text-[52px] font-bold leading-none mb-2" style={{ color: '#4d7cfe' }}>74</p>
          <p className="text-white/40 text-[12px]">out of 100</p>
        </div>
        <div className="rounded-xl p-6 text-center" style={{ background: 'rgba(77,124,254,0.08)', border: '1px solid rgba(77,124,254,0.3)' }}>
          <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">Overall Verdict</p>
          <p className="text-[18px] font-bold text-white mb-1">CMU more rigorous</p>
          <p className="text-white/40 text-[12px]">in 5 of 7 categories</p>
        </div>
        <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-center">
          <p className="text-[11px] tracking-widest uppercase text-white/30 mb-3">CMU Rigor Score</p>
          <p className="text-[52px] font-bold leading-none mb-2" style={{ color: '#f5a623' }}>87</p>
          <p className="text-white/40 text-[12px]">out of 100</p>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-white/10 bg-white/5 overflow-hidden mb-5">
        <div className="grid grid-cols-4 px-6 py-3 border-b border-white/10 text-[11px] font-semibold tracking-widest uppercase text-white/30">
          <div>Category</div><div>NYU</div><div>CMU</div><div>Δ Difference</div>
        </div>
        {tableData.map(row => (
          <div key={row.category} className="grid grid-cols-4 px-6 py-4 border-b border-white/5 last:border-0 items-center hover:bg-white/5 transition-colors">
            <div className="text-white/90 text-[14px] font-medium">{row.category}</div>
            <div className="text-[13px]" style={{ color: '#4d7cfe' }}>{row.a}</div>
            <div className="text-[13px]" style={{ color: '#f5a623' }}>{row.b}</div>
            <div>
              <span
                className="inline-block px-2.5 py-1 rounded-md text-[11px] font-semibold"
                style={{
                  background: row.winner === 'b' ? 'rgba(245,166,35,0.12)' : 'rgba(77,124,254,0.12)',
                  color: row.winner === 'b' ? '#f5a623' : '#6b8fff',
                  border: `1px solid ${row.winner === 'b' ? 'rgba(245,166,35,0.2)' : 'rgba(77,124,254,0.2)'}`,
                }}
              >
                {row.winner === 'b' ? 'B higher' : 'A higher'}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* AI Gap Analysis */}
      <div className="rounded-xl border border-white/10 bg-white/5 p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-[15px] font-semibold text-white">AI Gap Analysis</h3>
          <span className="text-[11px] font-bold px-2.5 py-1 rounded-full" style={{ background: 'rgba(255,77,106,0.15)', color: '#ff4d6a', border: '1px solid rgba(255,77,106,0.25)' }}>
            4 gaps identified
          </span>
        </div>
        <p className="text-[11px] text-white/30 mb-4">◆ All claims linked to source documents</p>
        {gaps.map(g => (
          <div key={g.title} className="rounded-lg p-4 mb-3 last:mb-0" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
            <p className="font-semibold text-white text-[13.5px] mb-1">{g.title}</p>
            <p className="text-white/50 text-[12.5px] mb-2">{g.body}</p>
            <p className="text-[11px] cursor-pointer hover:underline" style={{ color: '#4d7cfe' }}>📎 {g.cite}</p>
          </div>
        ))}
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