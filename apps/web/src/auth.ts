import NextAuth from "next-auth"
import type { NextAuthConfig } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"
import { loginSchema } from "@/lib/schema/auth"

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000"

export const authConfig = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const result = loginSchema.safeParse(credentials)
        if (!result.success) return null

        const { email, password } = result.data

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        })

        if (!response.ok) return null

        const user = await response.json()

        return {
          id: user.id || user.user_id,
          email: user.email,
          name: user.name,
          role: user.role || "default.user",
          accessToken: user.access_token, // from FastAPI
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      // on sign-in, copy user fields into token
      if (user) {
        token.id = user.id
        token.email = user.email
        token.name = user.name
        token.role = user.role
        token.accessToken = user.accessToken // may be undefined (optional)
      }
      return token
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
        session.user.email = token.email as string
        session.user.name = token.name as string
        session.user.role = token.role as string
      }

      // only set if present (prevents string|undefined errors)
      if (typeof token.accessToken === "string") {
        session.accessToken = token.accessToken
      }

      return session
    },
  },
  pages: {
    signIn: "/login",
    signOut: "/login",
    error: "/login",
  },
  session: { strategy: "jwt" },
  secret: process.env.AUTH_SECRET ?? process.env.NEXTAUTH_SECRET,
} satisfies NextAuthConfig

export const { handlers, auth, signIn, signOut } = NextAuth(authConfig)