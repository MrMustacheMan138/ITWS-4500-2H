import { auth } from "@/auth"


// Server-side session helper
export async function getSession() {
  return await auth()
}

export async function requireAuth() {
  const session = await getSession()
  if (!session) throw new Error("Unauthorized")
  return session
}

export async function getAccessToken() {
  const session = await getSession()
  return session?.accessToken
}