"use client";
import Link from "next/link";
import Image from "next/image";
import {
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs';

export const Navbar = () => {
  return (
    <div className="w-full fixed top-0 left-0 z-50 bg-white">
      <nav className="container relative flex flex-wrap items-center justify-between p-2 mx-auto lg:justify-between xl:px-1">
        Logo 
        <Link href="/">
          <span className="flex items-center space-x-2 text-2xl font-medium text-pink-500 dark:text-gray-100">
            <span>
              <Image
                src="/Bytebites.png"
                width="200"
                alt="logo"
                height="200"
                className="w-25 mt-2"
              />
            </span>
          </span>
        </Link>

        {/* User Profile */}
        <div className="gap-3 nav__item mr-2 lg:flex ml-auto lg:ml-0 lg:order-2">
          <div className="hidden mr-3 lg:flex nav__item">
            <SignedOut>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center">
                <div className="relative ml-4">
                  <UserButton
                    appearance={{
                      elements: {
                        userButton: {
                          width: '40px',
                          height: '40px',
                        },
                      },
                    }}
                  />
                  <div className="absolute right-0">
                    {/* Add dropdown menu items here */}
                  </div>
                </div>
              </div>
            </SignedIn>
          </div>
        </div>
      </nav>
    </div>
  );
}
