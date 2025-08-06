import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ToastProvider, ToastViewport } from "@/components/ui/toast"
import { Toaster } from "@/components/ui/toaster"

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'Fusion v15 - AI Agentic Operating System',
    description: 'ChatGPT-style interface for Fusion AI agents',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <ToastProvider>
                    {children}
                    <Toaster />
                    <ToastViewport />
                </ToastProvider>
            </body>
        </html>
    )
}