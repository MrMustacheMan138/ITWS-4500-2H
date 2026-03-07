// Landing page
import Header from "@/components/common/header"
import Link from "next/link";
// import all of the components

export default function Landing() {
   return (
      <div className="w-full h-full flex flex-col items-start justify-start min-h-screen">
         <Header />
         {/* CHANGE THE COLOR OF THE BACKGROUND. THIS IS JUST A PLACEHOLDER */}
         <main className="bg-gradient-to-r from-[#4F8EF7] to-[#3B72F6] w-full flex flex-col items-center justify-start grow">
            
            <div>   
               Benchmark Any University's Curriculum
            </div>

            <div>
            {/* INSTRUCTIONS ABOUT HOW TO USE THE APPLICATION HERE */}
            </div>

            <div>
               <Link
                  href=""
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded inline-block"
               > 
                  Start Comparing →
               </Link>
            </div>

            <div>
            {/* ADD BOXES WITH EXPLANATIONS AND HIGHLIGHTS ABOUT WHAT THIS APPLICATION DOES */}
            </div>

         </main>
      </div>
   );
}