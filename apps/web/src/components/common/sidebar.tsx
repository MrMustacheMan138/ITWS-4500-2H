'use client'
import { useEffect, useState } from 'react'
import { usePathname } from 'next/navigation'
import { getComparisonUsage } from '@/lib/api/endpoints'

const navItems = [
  { href: '/dashboard',              label: 'Dashboard',         icon: '⊟' },
  { href: '/dashboard/compare/new',  label: 'New Comparison',    icon: '+' },
  { href: '/dashboard/results',      label: 'Comparison Results',icon: '▦' },
  { href: '/dashboard/sources',      label: 'Sources',           icon: '⎙' },
  { href: '/dashboard/chat',         label: 'AI Chat',           icon: '◈' },
  { href: '/settings',               label: 'Settings',          icon: '⚙' },
]

type ComparisonUsage = {
  used: number
  limit: number
  remaining: number
}

export default function Sidebar() {
  const pathname = usePathname()
  const [usage, setUsage] = useState<ComparisonUsage | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadUsage() {
      try {
        const nextUsage = await getComparisonUsage()
        if (!cancelled) {
          setUsage(nextUsage)
        }
      } catch {
        if (!cancelled) {
          setUsage(null)
        }
      }
    }

    void loadUsage()

    return () => {
      cancelled = true
    }
  }, [])

  const used = usage?.used ?? 0
  const limit = usage?.limit ?? 20
  const progressPercent = limit > 0 ? Math.min((used / limit) * 100, 100) : 0

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col bg-[#111520] border-r border-[#1e2740]">
      <div className="p-5 border-b border-[#1e2740]">
        <div className="text-[11px] font-bold tracking-widest uppercase text-[#6b7a9e]">
          Curricompass
        </div>
        <div className="text-[15px] font-bold leading-tight mt-0.5 text-[#e8edf8] font-sans">
          Curriculum
          <br />
          Benchmarking
        </div>
      </div>

      <nav className="flex-1 py-3 overflow-y-auto">
        {navItems.map((item) => {
          const active = pathname === item.href
          return (
            <a
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 px-5 py-2.5 text-[13.5px] font-medium transition-all no-underline border-l-2 ${
                active
                  ? 'text-[#e8edf8] bg-[rgba(77,124,254,0.08)] border-l-[#4d7cfe]'
                  : 'text-[#6b7a9e] bg-transparent border-l-transparent'
              }`}
            >
              <span className={active ? 'opacity-100' : 'opacity-70'}>{item.icon}</span>
              {item.label}
            </a>
          )
        })}
      </nav>

      <div className="p-4 border-t border-[#1e2740]">
        <div className="rounded-xl p-3.5 bg-[rgba(245,166,35,0.08)] border border-[rgba(245,166,35,0.2)]">
          <div className="text-[12px] font-bold mb-1 text-[#f5a623]">Pro Plan</div>
          <div className="text-[11px] mb-2.5 text-[#6b7a9e]">
            {used} / {limit} comparisons used
          </div>
          <div className="h-1 rounded-full overflow-hidden bg-[#1e2740]">
            <div
              className="h-full rounded-full bg-[#f5a623]"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      </div>
    </aside>
  )
}
