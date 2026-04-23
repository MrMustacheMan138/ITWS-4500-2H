'use client';
import { getSession } from "@/lib/auth/session"
import Link from "next/link"
import { signOut, useSession } from 'next-auth/react';

export default function LoginButton() {
   const { data: session } = useSession();

   // Show sign-out when the user is logged in; otherwise link to login.
   return (
      <div>
         {session ? (
            <div className="flex items-center gap-3">
               <span className="text-sm text-slate-200">
                  Hi, {session.user.name?.trim() || session.user.email || "User"}
               </span>
               <button
                  type="button"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                  onClick={() => signOut({ callbackUrl: '/login' })}
               >
                  Sign Out
               </button>
            </div>
         ) : (
            <Link
               href="/login"
               className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded inline-block"
            >
               Sign In
            </Link>
         )}
      </div>
   );
}