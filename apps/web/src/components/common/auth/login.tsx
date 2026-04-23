'use client';

import Link from 'next/link';
import { signOut, useSession } from 'next-auth/react';

export default function LoginButton() {
   const { data: session } = useSession();

   // Show sign-out when the user is logged in; otherwise link to login.
   return (
      <div>
         {session ? (
               <button
                  type="button"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                  onClick={() => signOut({ callbackUrl: '/login' })}
               >
                  Sign Out
               </button>
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