import type { Metadata } from 'next'
import './globals.css'
import { Providers } from './providers'
import { DM_Sans } from 'next/font/google'

export const metadata: Metadata = {
  title: 'Curriculum Comparison Tool',
  description: 'Compare academic programs and curricula',
};

const dmSans = DM_Sans({subsets: ['latin']})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={dmSans.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
