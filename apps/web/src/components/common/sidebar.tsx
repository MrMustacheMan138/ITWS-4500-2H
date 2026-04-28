'use client'
import { usePathname } from 'next/navigation'

const navItems = [
  { href: '/dashboard',              label: 'Dashboard',         icon: '⊟' },
  { href: '/dashboard/compare/new',  label: 'New Comparison',    icon: '+' },
  { href: '/dashboard/results',      label: 'Comparison Results',icon: '▦' },
  { href: '/dashboard/sources',      label: 'Sources',           icon: '⎙' },
  { href: '/dashboard/chat',         label: 'AI Chat',           icon: '◈' },
  { href: '/settings',               label: 'Settings',          icon: '⚙' },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 flex flex-col bg-[#111520] border-r border-[#1e2740]">
      {/* Logo */}
      <div className="p-5 border-b border-[#1e2740]">
        <div className="text-[11px] font-bold tracking-widest uppercase text-[#6b7a9e]">Curricompass</div>
        <div className="text-[15px] font-bold leading-tight mt-0.5 text-[#e8edf8] font-sans">
          Curriculum<br />Benchmarking
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto">
        {navItems.map(item => {
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

      {/* Plan badge */}
      <div className="p-4 border-t border-[#1e2740]">
        <div className="rounded-xl p-3.5 bg-[rgba(245,166,35,0.08)] border border-[rgba(245,166,35,0.2)]">
          <div className="text-[12px] font-bold mb-1 text-[#f5a623]">Pro Plan</div>
          <div className="text-[11px] mb-2.5 text-[#6b7a9e]">12 / 20 comparisons used</div>
          <div className="h-1 rounded-full overflow-hidden bg-[#1e2740]">
            <div className="h-full w-3/5 rounded-full bg-[#f5a623]" />
          </div>
        </div>
      </div>
    </aside>
  )
}
