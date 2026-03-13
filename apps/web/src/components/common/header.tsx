import Image from "next/image"
import logo from "@/assets/syllabusai.png"
import LoginButton from "./auth/login"

export default function Header() {
  return (
    <header
      className="w-full flex items-center justify-start px-6 py-3 sticky top-0 z-40"
      style={{ background: '#0a0d14', borderBottom: '1px solid #1e2740', minHeight: 56 }}
    >
      {/* Logo */}
      <div className="flex items-center gap-2">
        <Image src={logo} alt="Project Logo" width={36} height={36} />
        <div>
          <div className="text-[11px] font-bold tracking-widest uppercase" style={{ color: '#4d7cfe' }}>
            Curricompass
          </div>
          <div className="text-[13px] font-semibold" style={{ color: '#e8edf8' }}>
            AI Curriculum Benchmarking
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="ml-auto flex items-center gap-3">
        <span className="text-[13px]" style={{ color: '#6b7a9e' }}>NYU Workspace</span>
        <LoginButton />
      </div>
    </header>
  )
}