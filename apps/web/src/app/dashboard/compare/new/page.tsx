// New Comparison page
import Header from "@/components/common/header"
import Sidebar from "@/components/common/sidebar"

export default function ComparePage () {
   return (
      <div className="flex min-h-screen">
         <Sidebar />
      
         <div className="flex-1 ml-64 flex flex-col">
            <Header />
            
            <main className="flex-1 p-6">
               {/* COMPARE FORM WILL BE IMPORTED HERE */}
               <h1>Compare page</h1>
            </main>
         </div>
      </div>
   );
}