// Landing page
import Header from "@/components/common/header"
import Link from "next/link"

const features = [
  {
    icon: '⊟',
    title: 'Side-by-Side Comparison',
    color: '#4d7cfe',
    desc: 'Parallel tables for requirements, tracks, and course depth across two institutions.',
  },
  {
    icon: '◈',
    title: 'Citation-Grounded AI',
    color: '#f5a623',
    desc: 'Every AI insight links directly to the source document — no hallucinations, no guesswork.',
  },
  {
    icon: '✏',
    title: 'Markup & Annotate',
    color: '#29d987',
    desc: 'Highlight gaps, add notes, and share annotated comparisons with your committee.',
  },
]

export default function Landing() {
  return (
    <div className="w-full flex flex-col min-h-screen" style={{ background: '#0a0d14' }}>
      <Header />

      <main className="flex flex-col items-center flex-1">

        {/* Hero */}
        <div
          className="w-full flex flex-col items-center justify-center text-center px-6 py-28"
          style={{
            background: 'radial-gradient(ellipse 80% 50% at 50% 20%, rgba(77,124,254,0.12) 0%, transparent 70%)',
          }}
        >
          {/* Badge */}
          <div
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-[12px] font-semibold mb-7"
            style={{ background: 'rgba(77,124,254,0.1)', border: '1px solid rgba(77,124,254,0.3)', color: '#6b8fff', letterSpacing: '0.05em' }}
          >
            ◆ AI-Powered · Citation-Grounded
          </div>

          {/* Headline */}
          <h1 className="text-[clamp(42px,6vw,72px)] font-extrabold leading-tight mb-5" style={{ color: '#e8edf8' }}>
            Benchmark Any<br />
            <span style={{ color: '#4d7cfe' }}>University Curriculum</span>
          </h1>

          {/* Subheading */}
          <p className="text-[17px] max-w-lg mb-10 leading-relaxed" style={{ color: '#6b7a9e' }}>
            Paste course catalog links, PDFs, or text and get a side-by-side comparison with verifiable citations — in seconds.
          </p>

          {/* CTAs */}
          <div className="flex gap-3 flex-wrap justify-center">
            <Link
              href="/dashboard/compare/new"
              className="px-7 py-3 rounded-xl text-[15px] font-medium text-white transition-all hover:-translate-y-0.5"
              style={{ background: '#4d7cfe' }}
            >
              Start Comparing →
            </Link>
            <Link
              href="/dashboard"
              className="px-7 py-3 rounded-xl text-[15px] font-medium transition-colors"
              style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid #1e2740', color: '#e8edf8' }}
            >
              View Dashboard
            </Link>
          </div>
        </div>

        {/* Feature cards */}
        <div className="grid grid-cols-3 gap-4 px-10 pb-20 w-full max-w-5xl">
          {features.map(f => (
            <div
              key={f.title}
              className="rounded-2xl p-7 transition-colors"
              style={{ background: '#111520', border: '1px solid #1e2740' }}
            >
              <div className="text-[22px] mb-4">{f.icon}</div>
              <h3 className="text-[15px] font-semibold mb-2" style={{ color: f.color }}>{f.title}</h3>
              <p className="text-[13px] leading-relaxed" style={{ color: '#6b7a9e' }}>{f.desc}</p>
            </div>
          ))}
        </div>

      </main>
    </div>
  )
}