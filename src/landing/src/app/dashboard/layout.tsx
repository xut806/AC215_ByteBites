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
      <div className="bg-pink-50 min-h-screen flex flex-col mt-10">
        <main className="container mx-auto flex-grow flex flex-col items-center justify-center sm:p-4 lg:p-8">
          <div className="w-full max-w-2xl">
            <div className="mb-2 text-center">
              <Image
                src="/img/logo.png"
                alt="ByteBites Logo"
                width={250}
                height={250}
                className="mx-auto mb-2 h-50"
              />
            </div>
            {children}
          </div>
        </main>
      </div>
    );
  }
  
