import type { Metadata } from "next";
import { Geist_Mono, Montserrat, Open_Sans } from "next/font/google";

import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";

import "./globals.css";

const openSans = Open_Sans({
  variable: "--font-open-sans",
  subsets: ["latin"],
  display: "swap",
});

const montserrat = Montserrat({
  variable: "--font-montserrat",
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
      className={`${openSans.variable} ${montserrat.variable} ${geistMono.variable} h-full`}
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
