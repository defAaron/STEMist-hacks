import type { Metadata } from "next";
import { Figtree, Geist_Mono, Syne } from "next/font/google";

import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

import "./globals.css";

const figtree = Figtree({
  variable: "--font-figtree",
  subsets: ["latin"],
  display: "swap",
});

const syne = Syne({
  variable: "--font-syne",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "HoneyDesk",
    template: "%s · HoneyDesk",
  },
  description:
    "Trap the scammer. Teach the student. Brief the school. A defensive honeypot for student threats.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${figtree.variable} ${syne.variable} ${geistMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col">
        <TooltipProvider delayDuration={200}>
          {children}
          <Toaster theme="light" position="bottom-right" richColors closeButton />
        </TooltipProvider>
      </body>
    </html>
  );
}
