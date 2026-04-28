'use client'

import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { sendChatMessage } from '@/lib/api/endpoints'

type Message = {
  role: 'user' | 'ai'
  text: string
}

const WELCOME: Message = {
  role: 'ai',
  text: "Hi! I'm your AI curriculum assistant. Ask me anything about your program comparisons — gaps, course requirements, rigor differences, or anything else.",
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([WELCOME])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const searchParams = useSearchParams()
  const comparisonId = searchParams.get('id')

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const send = async () => {
    const text = input.trim()
    if (!text || typing) return

    const userMsg: Message = { role: 'user', text }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setTyping(true)

    const history = messages
      .filter(m => m.text !== WELCOME.text)
      .map(m => ({
        role: (m.role === 'ai' ? 'model' : 'user') as 'user' | 'model',
        content: m.text,
      }))

    try {
      const data = await sendChatMessage(
        text,
        history,
        comparisonId ? Number(comparisonId) : undefined
      )
      setMessages(prev => [...prev, { role: 'ai', text: data.reply }])
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        { role: 'ai', text: `Sorry, something went wrong: ${err?.message ?? 'Unknown error'}` },
      ])
    } finally {
      setTyping(false)
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 px-6 py-3 border-b border-white/10 flex-shrink-0">
        <span className="text-[11px] font-semibold tracking-widest uppercase text-white/30">AI Chat</span>
        <span
          className="px-3 py-1 rounded-full text-[12px] font-semibold"
          style={{ border: '1px solid #29d987', color: '#29d987', background: 'rgba(41,217,135,0.08)' }}
        >
          Gemini powered
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div style={{ maxWidth: msg.role === 'user' ? '60%' : '75%' }}>
              <div
                className="text-[14px] leading-relaxed whitespace-pre-wrap"
                style={{
                  background: msg.role === 'user' ? '#4d7cfe' : 'rgba(255,255,255,0.05)',
                  border: msg.role === 'ai' ? '1px solid rgba(255,255,255,0.1)' : 'none',
                  padding: msg.role === 'user' ? '12px 18px' : '18px 20px',
                  borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                  color: '#fff',
                }}
              >
                {msg.text}
              </div>
            </div>
          </div>
        ))}

        {typing && (
          <div className="flex justify-start">
            <div className="px-4 py-3 rounded-2xl" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/40 mr-1 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/40 mr-1 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-white/40 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="px-6 py-4 border-t border-white/10 flex-shrink-0">
        <div className="flex gap-3 items-center">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
            rows={1}
            placeholder="Ask about the curriculum comparison..."
            className="flex-1 rounded-xl px-4 py-3 text-[14px] text-white placeholder-white/25 outline-none resize-none"
            style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
          />
          <button
            onClick={send}
            disabled={typing}
            className="w-11 h-11 rounded-xl flex items-center justify-center text-white text-lg flex-shrink-0 hover:-translate-y-0.5 transition-transform disabled:opacity-40 disabled:cursor-not-allowed"
            style={{ background: '#4d7cfe' }}
          >
            →
          </button>
        </div>
      </div>
    </div>
  )
}