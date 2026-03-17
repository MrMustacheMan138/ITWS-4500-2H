'use client'
import { useState, useRef, useEffect } from 'react'

type Message = {
  role: 'user' | 'ai'
  text: string
  cards?: { title: string; body: string; cite: string }[]
}

const initialMessages: Message[] = [
  {
    role: 'user',
    text: "What are the biggest curriculum gaps between NYU and CMU's CS programs?",
  },
  {
    role: 'ai',
    text: 'Based on the sources you provided, here are the three most significant gaps identified:',
    cards: [
      { title: 'Distributed Systems', body: 'CMU offers a structured 4-course track; NYU has no equivalent concentration.', cite: 'CMU SCS Catalog 2024, p. 34' },
      { title: 'Prerequisite Depth',  body: "CMU's algorithms sequence averages 3.8 prerequisite levels vs. NYU's 2.1.", cite: 'NYU Bulletin 2024-25' },
      { title: 'Theory Emphasis',     body: 'CMU requires 3 dedicated theory courses; NYU requires 1.', cite: 'Both course catalogs, cross-referenced' },
    ],
  },
  {
    role: 'user',
    text: 'Can you suggest how NYU could close the Distributed Systems gap?',
  },
  {
    role: 'ai',
    text: "Based on CMU's track structure (cited: CMU SCS Catalog 2024, p. 34-36), NYU could introduce a Distributed Systems concentration with the following 4-course sequence:",
    cards: [
      { title: 'DS 101 — Introduction to Distributed Systems', body: 'Prerequisite: Operating Systems. Covers CAP theorem, consensus algorithms, and fault tolerance basics.', cite: '' },
      { title: 'DS 201 — Distributed Storage & Databases',     body: 'Covers consistent hashing, replication strategies, and eventual consistency models.', cite: '' },
    ],
  },
]

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  const send = () => {
    const text = input.trim()
    if (!text) return
    setMessages(prev => [...prev, { role: 'user', text }])
    setInput('')
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      setMessages(prev => [...prev, {
        role: 'ai',
        text: 'Based on the loaded sources, I can analyze that aspect of the NYU vs CMU curriculum. Would you like me to break it down by credit hours, course sequence, or program outcomes?',
      }])
    }, 1400)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Context bar */}
      <div className="flex items-center gap-3 px-6 py-3 border-b border-white/10 flex-shrink-0">
        <span className="text-[11px] font-semibold tracking-widest uppercase text-white/30">Context:</span>
        <span className="px-3 py-1 rounded-full text-[12px] font-semibold cursor-pointer" style={{ border: '1px solid #4d7cfe', color: '#4d7cfe', background: 'rgba(77,124,254,0.08)' }}>
          NYU vs CMU — B.S. CS
        </span>
        <span className="px-3 py-1 rounded-full text-[12px] font-semibold cursor-pointer" style={{ border: '1px solid #29d987', color: '#29d987', background: 'rgba(41,217,135,0.08)' }}>
          8 sources loaded
        </span>
        <button className="ml-auto text-[12px] text-white/40 border border-white/10 px-3 py-1 rounded-full hover:border-white/30 transition-colors">
          + Add Source
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-5 flex flex-col gap-5">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div style={{ maxWidth: msg.role === 'user' ? '60%' : '75%' }}>
              <div
                className="text-[14px] leading-relaxed"
                style={{
                  background: msg.role === 'user' ? '#4d7cfe' : 'rgba(255,255,255,0.05)',
                  border: msg.role === 'ai' ? '1px solid rgba(255,255,255,0.1)' : 'none',
                  padding: msg.role === 'user' ? '12px 18px' : '18px 20px',
                  borderRadius: msg.role === 'user' ? '14px 14px 4px 14px' : '14px 14px 14px 4px',
                  color: '#fff',
                }}
              >
                {msg.text && <p className={msg.cards?.length ? 'mb-3' : ''}>{msg.text}</p>}
                {msg.cards?.map(c => (
                  <div key={c.title} className="rounded-lg p-3 mb-2 last:mb-0" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <p className="font-semibold text-[13px] mb-1 text-white">{c.title}</p>
                    <p className="text-white/50 text-[12px] mb-1.5">{c.body}</p>
                    {c.cite && <p className="text-[11px] cursor-pointer hover:underline" style={{ color: '#4d7cfe' }}>📎 {c.cite}</p>}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
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

      {/* Input */}
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
            className="w-11 h-11 rounded-xl flex items-center justify-center text-white text-lg flex-shrink-0 hover:-translate-y-0.5 transition-transform"
            style={{ background: '#4d7cfe' }}
          >
            →
          </button>
        </div>
      </div>
    </div>
  )
}