import React from "react";
import { Container } from "@/components/Container";
import { SignInButton } from '@clerk/nextjs';

export const Cta = () => {
  return (
    <Container>
      <div className="flex flex-col items-center justify-center w-full bg-pink-100 px-7 py-12 text-center">
        <h2 className="text-3xl font-bold text-gray-800">
          Ready to transform your groceries and <span className="text-pink-600">elevate your meals</span>?
        </h2>
        <p className="mt-4 text-lg text-gray-600">
          Join thousands of users already creating personalized, nutritious recipes with ByteBites.
        </p>
        <div className="mt-6">
          <div className="px-8 py-4 text-lg font-medium text-center text-white bg-pink-600 rounded-md">
            <SignInButton>
              Discover Your Meals Today →
            </SignInButton>
          </div>
        </div>
      </div>
    </Container>
  );
};
