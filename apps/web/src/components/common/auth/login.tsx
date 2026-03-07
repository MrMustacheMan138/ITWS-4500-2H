import { getSession } from "@/lib/auth/session"
import Link from "next/link"

export default async function LoginButton() {
   const session = await getSession();
   // If sessions exists, present the user with a "Sign Out" button and "Sign In" button if it doesn't
   return (
      <div>
         {session ? (
            <form action="/api/auth/signout" method="POST">
               <button 
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
               >
                  Sign Out
               </button>
            </form>
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