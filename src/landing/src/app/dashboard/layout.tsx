import type { Metadata } from "next"
import "./../globals.css"
import Image from "next/image"
import {
    ClerkProvider,
    SignedIn,
    SignedOut,
    UserButton
  } from '@clerk/nextjs';
import { Navbar } from './_components/TopNav';

export const metadata: Metadata = {
  title: "ByteBites - Your Cooking Assistant",
  description: "ByteBites helps you create delicious recipes from your groceries",
}

export default function DashboardLayout({
    children,
  }: {
    children: React.ReactNode;
  }) {
    return (
      <div className="min-h-screen bg-[#fdf2f8]">
        <main className="container mx-auto flex min-h-screen flex-col items-center justify-center p-4">
          <div className="w-full max-w-2xl">
            <div className="mb-8 text-center">
              <Image
                src="/img/logo.png"
                alt="ByteBites Logo"
                width={300}
                height={300}
                className="mx-auto mb-6 h-100"
              />
            </div>
            {children}
          </div>
        </main>
      </div>
    );
  }
  
