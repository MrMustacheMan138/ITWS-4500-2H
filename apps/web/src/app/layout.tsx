import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import { DM_Sans } from 'next/font/google'
import syllabusAiLogo from '../assets/syllabusai.png'

export const metadata: Metadata = {
  title: 'Curriculum Comparison Tool',
  description: 'Compare academic programs and curricula',
  icons: {
    icon: syllabusAiLogo.src,
    shortcut: syllabusAiLogo.src,
    apple: syllabusAiLogo.src,
  },
}

const dmSans = DM_Sans({subsets: ['latin']})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${dmSans.className} bg-slate-950 text-slate-100`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
