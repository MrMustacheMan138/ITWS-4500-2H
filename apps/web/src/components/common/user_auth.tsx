'use client'
/**
 * UserAuth: authenticated user menu for the header.
 *
 * Shows the user's avatar, name, and role. Clicking opens a dropdown
 * with profile/settings links (role-gated via rbac.ts) and a sign-out button.
 *
 * Falls back to a Sign In link when the user is not authenticated.
 */
import Link from 'next/link'
import { useState, useRef, useEffect } from 'react'
import { signOut, useSession } from 'next-auth/react'
import { hasPermission, isAdmin, normalizeRole, PERMISSIONS } from '@/lib/auth/rbac'

export default function UserAuth() {
  const { data: session, status } = useSession()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Loading skeleton
  if (status === 'loading') {
    return (
      <div className="h-9 w-24 rounded-lg animate-pulse" style={{ background: '#1e2740' }} />
    )
  }

  // Unauthenticated
  if (!session?.user) {
    return (
      <Link
        href="/login"
        className="px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors"
        style={{ background: '#4d7cfe' }}
      >
        Sign In
      </Link>
    )
  }

  const user = session.user
  const role = normalizeRole(user.role)
  const displayName = user.name?.trim() || user.email?.split('@')[0] || 'User'
  const initial = displayName.charAt(0).toUpperCase()

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5"
      >
        {/* Avatar */}
        <div
          className="flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold text-white"
          style={{ background: '#4d7cfe' }}
        >
          {initial}
        </div>
        {/* Name + role */}
        <div className="text-left hidden sm:block">
          <div className="text-[13px] font-medium leading-tight" style={{ color: '#e8edf8' }}>
            {displayName}
          </div>
          <div className="text-[10px] capitalize" style={{ color: '#6b7a9e' }}>
            {role.replace('default.', '')}
          </div>
        </div>
        {/* Chevron */}
        <span
          className="text-xs transition-transform"
          style={{
            color: '#6b7a9e',
            transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          ▾
        </span>
      </button>

      {/* Dropdown */}
      {open && (
        <div
          className="absolute right-0 mt-2 w-56 rounded-xl overflow-hidden z-50"
          style={{ background: '#111520', border: '1px solid #1e2740' }}
        >
          {/* Header */}
          <div className="px-4 py-3" style={{ borderBottom: '1px solid #1e2740' }}>
            <div className="text-[13px] font-medium truncate" style={{ color: '#e8edf8' }}>
              {displayName}
            </div>
            <div className="text-[11px] truncate" style={{ color: '#6b7a9e' }}>
              {user.email}
            </div>
          </div>

          {/* Menu items */}
          <div className="py-1">
            <MenuItem href="/dashboard" label="Dashboard" icon="⊟" onClick={() => setOpen(false)} />
            <MenuItem href="/settings"  label="Settings"  icon="⚙" onClick={() => setOpen(false)} />

            {/* Admin-only */}
            {isAdmin(role) && (
              <MenuItem
                href="/admin/users"
                label="Manage Users"
                icon="👥"
                onClick={() => setOpen(false)}
              />
            )}

            {/* Permission-gated example */}
            {hasPermission(role, PERMISSIONS.COMPARISON_CREATE) && (
              <MenuItem
                href="/dashboard/compare/new"
                label="New Comparison"
                icon="+"
                onClick={() => setOpen(false)}
              />
            )}
          </div>

          {/* Sign out */}
          <div style={{ borderTop: '1px solid #1e2740' }}>
            <button
              onClick={() => signOut({ callbackUrl: '/login' })}
              className="flex items-center gap-2.5 w-full px-4 py-2.5 text-[13px] text-left transition-colors hover:bg-white/5"
              style={{ color: '#f87171' }}
            >
              <span>↗</span>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function MenuItem({
  href,
  label,
  icon,
  onClick,
}: {
  href: string
  label: string
  icon: string
  onClick?: () => void
}) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className="flex items-center gap-2.5 px-4 py-2.5 text-[13px] transition-colors hover:bg-white/5"
      style={{ color: '#a0aec8' }}
    >
      <span style={{ color: '#6b7a9e' }}>{icon}</span>
      {label}
    </Link>
  )
}