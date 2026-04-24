/**
 * Role-Based Access Control (RBAC)
 *
 * Defines roles, permissions, and helper functions for checking
 * whether a user can perform a given action.
 *
 * Role strings match what the FastAPI backend returns on login
 * (see auth.ts — `role: user.role || "default.user"`).
 */

// ---------------------------------------------------------------------------
// Role definitions
// ---------------------------------------------------------------------------

export const ROLES = {
    ADMIN: 'admin',
    USER: 'default.user',
    GUEST: 'guest',
  } as const
  
  export type Role = (typeof ROLES)[keyof typeof ROLES]
  
  /** Hierarchy — higher number = more privileges. */
  const ROLE_HIERARCHY: Record<Role, number> = {
    [ROLES.ADMIN]: 100,
    [ROLES.USER]: 10,
    [ROLES.GUEST]: 0,
  }
  
  // ---------------------------------------------------------------------------
  // Permission definitions
  // ---------------------------------------------------------------------------
  
  export const PERMISSIONS = {
    // Sources
    SOURCE_VIEW:   'source:view',
    SOURCE_CREATE: 'source:create',
    SOURCE_UPDATE: 'source:update',
    SOURCE_DELETE: 'source:delete',
  
    // Comparisons
    COMPARISON_VIEW:   'comparison:view',
    COMPARISON_CREATE: 'comparison:create',
    COMPARISON_DELETE: 'comparison:delete',
  
    // Admin-only
    USER_MANAGE:     'user:manage',
    SYSTEM_SETTINGS: 'system:settings',
  } as const
  
  export type Permission = (typeof PERMISSIONS)[keyof typeof PERMISSIONS]
  
  /** Which permissions each role gets. */
  const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
    [ROLES.ADMIN]: Object.values(PERMISSIONS),
    [ROLES.USER]: [
      PERMISSIONS.SOURCE_VIEW,
      PERMISSIONS.SOURCE_CREATE,
      PERMISSIONS.SOURCE_UPDATE,
      PERMISSIONS.SOURCE_DELETE,
      PERMISSIONS.COMPARISON_VIEW,
      PERMISSIONS.COMPARISON_CREATE,
      PERMISSIONS.COMPARISON_DELETE,
    ],
    [ROLES.GUEST]: [],
  }
  
  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  
  /** Normalize an unknown role string to a known Role, defaulting to GUEST. */
  export function normalizeRole(role: string | undefined | null): Role {
    if (!role) return ROLES.GUEST
    return (Object.values(ROLES) as string[]).includes(role) ? (role as Role) : ROLES.GUEST
  }
  
  /** Check whether a role has at least the privileges of `minimum`. */
  export function hasRole(role: string | undefined | null, minimum: Role): boolean {
    const r = normalizeRole(role)
    return ROLE_HIERARCHY[r] >= ROLE_HIERARCHY[minimum]
  }
  
  /** Check whether a role has a specific permission. */
  export function hasPermission(
    role: string | undefined | null,
    permission: Permission
  ): boolean {
    const r = normalizeRole(role)
    return ROLE_PERMISSIONS[r].includes(permission)
  }
  
  /** Check if a role has ALL of the given permissions. */
  export function hasAllPermissions(
    role: string | undefined | null,
    permissions: Permission[]
  ): boolean {
    return permissions.every(p => hasPermission(role, p))
  }
  
  /** Check if a role has ANY of the given permissions. */
  export function hasAnyPermission(
    role: string | undefined | null,
    permissions: Permission[]
  ): boolean {
    return permissions.some(p => hasPermission(role, p))
  }
  
  /** Shortcut: is this role an admin? */
  export function isAdmin(role: string | undefined | null): boolean {
    return normalizeRole(role) === ROLES.ADMIN
  }