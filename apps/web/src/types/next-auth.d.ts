import "next-auth"
import { DefaultSession, DefaultUser } from "next-auth";
import "next-auth/jwt"
import { DefaultJWT } from "next-auth/jwt";

declare module "next-auth" {
  interface Session extends DefaultSession {
    user: DefaultSession["user"] & {
      id: string
      role: string
    };
    accessToken?: string;
  }

  interface User extends DefaultUser {
    id: string
    role: string
    accessToken?: string
  }
}

declare module 'next-auth/jwt' {
  interface JWT extends DefaultJWT {
    id?: string
    role?: string
    accessToken?: string
  }
}
