import Header from "@/components/common/header"
import Sidebar from "@/components/common/sidebar"
import ResultsView from "@/components/comparison/ResultsView"

export default function ResultsPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 p-6">
          <ResultsView />
        </main>
      </div>
    </div>
  )
}