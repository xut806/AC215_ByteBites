import type { Metadata } from "next"
import "./../globals.css"
import Image from "next/image"

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
      <div className="bg-pink-50">
        <main className="container mx-auto flex min-h-screen flex-col items-center justify-center">
          <div className="w-full max-w-2xl">
            <div className="mb-4 text-center">
              <Image
                src="/img/logo.png"
                alt="ByteBites Logo"
                width={250}
                height={250}
                className="mx-auto mb-4 h-100"
              />
            </div>
            {children}
          </div>
        </main>
      </div>
    );
  }
  
