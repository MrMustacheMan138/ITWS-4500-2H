export default function Sidebar() {
   return (
      <aside className="border-2 border-gray-700 bg-gray-800 text-white h-screen w-64 fixed left-0 top-0 flex flex-col">
         <div className="p-4 border-b border-gray-700">
            <h2 className="text-xl font-bold">Navigation</h2>
         </div>
         <nav className="flex-1 p-4">
            {/* Add navigation items here */}
            <ul className="space-y-2">
               <li>
                  <a href="/dashboard" className="block p-2 hover:bg-gray-800 rounded">
                     Dashboard
                  </a>
               </li>
               <li>
                  <a href="/dashboard/compare/new" className="block p-2 hover:bg-gray-800 rounded">
                     Compare
                  </a>
               </li>
            </ul>
         </nav>
      </aside>
   );
}