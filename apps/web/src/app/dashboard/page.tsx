// Dashboard page

import Header from "@/components/common/header"
import Sidebar from "@/components/common/sidebar";

export default function Dashboard () {
   return (
      <div className="flex min-h-screen">
               <Sidebar />
            
               <div className="flex-1 ml-64 flex flex-col">
                  <Header />
                  
                  <main className="flex-1 p-6">
                     {/* Dashboard FORM WILL BE IMPORTED HERE */}
                     <h1>Dashboard page</h1>
                  </main>
               </div>
            </div>
   );
}