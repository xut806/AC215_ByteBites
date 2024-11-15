"use client";
import Link from "next/link";
import ThemeChanger from "./DarkSwitch";
import Image from "next/image";
import { Disclosure } from "@headlessui/react";
import {
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton,
} from '@clerk/nextjs';

export const Navbar = () => {
  const navigation = [
    "Product",
    "Features", 
    "How it works",
    "Blog",
  ];

  return (
    <div className="w-full fixed top-0 left-0 z-50 bg-white">
      <nav className="container relative flex flex-wrap items-center justify-between p-2 mx-auto lg:justify-between xl:px-1">
        {/* Logo  */}
        <Link href="/">
          <span className="flex items-center space-x-2 text-2xl font-medium text-pink-500 dark:text-gray-100">
            <span>
              <Image
                src="/img/logo.svg"
                width="32"
                alt="N"
                height="32"
                className="w-8"
              />
            </span>
            <span>ByteBites</span>
          </span>
        </Link>

        {/* Sign In / User Menu */}
        <div className="gap-3 nav__item mr-2 lg:flex ml-auto lg:ml-0 lg:order-2">
          <ThemeChanger />
          <div className="hidden mr-3 lg:flex nav__item">
            <SignedOut>
              <SignInButton className="px-6 py-2 text-white bg-pink-600 rounded-md md:ml-5 hover:bg-pink-700 transition duration-300">
                Get Started
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="relative">
                <UserButton
                  className="flex items-center justify-center w-10 h-10 rounded-full"
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
            </SignedIn>
          </div>
        </div>
                
        <Disclosure>
          {({ open }) => (
            <>
                <Disclosure.Button
                  aria-label="Toggle Menu"
                  className="px-2 py-1 text-gray-500 rounded-md lg:hidden hover:text-pink-500 focus:text-pink-500 focus:bg-pink-100 focus:outline-none dark:text-gray-300 dark:focus:bg-trueGray-700">
                  <svg
                    className="w-6 h-6 fill-current"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24">
                    {open && (
                      <path
                        fillRule="evenodd"
                        clipRule="evenodd"
                        d="M18.278 16.864a1 1 0 0 1-1.414 1.414l-4.829-4.828-4.828 4.828a1 1 0 0 1-1.414-1.414l4.828-4.829-4.828-4.828a1 1 0 0 1 1.414-1.414l4.829 4.828 4.828-4.828a1 1 0 1 1 1.414 1.414l-4.828 4.829 4.828 4.828z"
                      />
                    )}
                    {!open && (
                      <path
                        fillRule="evenodd"
                        d="M4 5h16a1 1 0 0 1 0 2H4a1 1 0 1 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2zm0 6h16a1 1 0 0 1 0 2H4a1 1 0 0 1 0-2z"
                      />
                    )}
                  </svg>
                </Disclosure.Button>

                <Disclosure.Panel className="flex flex-wrap w-full my-5 lg:hidden">
                  <>
                    {navigation.map((item, index) => (
                      <Link key={index} href={typeof item === 'string' ? "/" : item.href} className="w-full px-4 py-2 -ml-4 text-gray-500 rounded-md dark:text-gray-300 hover:text-pink-500 focus:text-pink-500 focus:bg-pink-100 dark:focus:bg-gray-800 focus:outline-none">
                          {typeof item === 'string' ? item : item.name}
                      </Link>
                    ))}
                    <SignedOut>
                      <SignInButton className="w-full px-6 py-2 mt-3 text-center text-white bg-pink-600 rounded-md lg:ml-5 hover:bg-pink-700 transition duration-300">
                        Get Started
                      </SignInButton>
                    </SignedOut>
                    <SignedIn>
                      <Link href="/dashboard" className="w-full px-6 py-2 mt-3 text-center text-white bg-pink-600 rounded-md lg:ml-5 hover:bg-pink-700 transition duration-300">
                        Dashboard
                      </Link>
                    </SignedIn>
                  </>
                </Disclosure.Panel>
            </>
          )}
        </Disclosure>
        
        {/* menu  */}
        <div className="hidden text-center lg:flex lg:items-center">
          <ul className="items-center justify-end flex-1 pt-6 list-none lg:pt-0 lg:flex">
            {navigation.map((item, index) => (
              <li className="mr-3 nav__item" key={index}>
                <Link href={typeof item === 'string' ? "/" : item.href} className="inline-block px-4 py-2 text-lg font-normal text-gray-800 no-underline rounded-md dark:text-gray-200 hover:text-pink-500 focus:text-pink-500 focus:bg-pink-100 focus:outline-none dark:focus:bg-gray-800">
                  {typeof item === 'string' ? item : item.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

      </nav>
    </div>
  );
}

