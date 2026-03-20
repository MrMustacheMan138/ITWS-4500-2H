import { getSession } from "@/lib/auth/session"
import { signOut } from "@/auth"
import Link from "next/link"

export default async function LoginButton() {
   const session = await getSession();
   // If sessions exists, present the user with a "Sign Out" button and "Sign In" button if it doesn't
   return (
      <div>
         {session ? (
            <div className="flex items-center gap-3">
               <span className="text-sm text-slate-200">
                  Hi, {session.user.name?.trim() || session.user.email || "User"}
               </span>
               <form
                  action={async () => {
                     "use server"
                     await signOut({ redirectTo: "/login" })
                  }}
               >
                  <button 
                     type="submit"
                     className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
                  >
                     Sign Out
                  </button>
               </form>
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