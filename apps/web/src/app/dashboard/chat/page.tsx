import Header from '@/components/common/header'
import Sidebar from '@/components/common/sidebar'
import ChatView from '@/components/comparison/ChatView'

export default function ChatPage() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64 flex flex-col">
        <Header />
        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatView />
        </main>
      </div>
    </div>
  )
}
