import Image from "next/image";
import { Container } from "@/components/Container";
import heroImg from "../../public/img/hero.png";
import { SignInButton } from '@clerk/nextjs';

export const Hero = () => {
  return (
    <>
      <Container className="flex flex-wrap mt-20">
        <div className="flex items-center w-full lg:w-1/2 pl-10 pt-8">
          <div className="max-w-2xl mb-8">
            <h1 className="text-4xl font-bold leading-snug tracking-tight text-gray-800 lg:text-4xl lg:leading-tight xl:text-6xl xl:leading-tight dark:text-white">
              Your Perfect Recipe in Seconds
            </h1>
            <p className="py-5 text-2lg leading-normal text-gray-500 lg:text-xl xl:text-2lg dark:text-gray-300">
              ByteBites transforms your groceries into personalized, nutritious meals. 
              Powered by AI and OCR, it creates recipes tailored to your lifestyle, 
              helping you eat smarter, save time, and make every ingredient count.
            </p>

            <div className="flex flex-col items-start space-y-3 sm:space-x-4 sm:space-y-0 sm:items-center sm:flex-row">
              <div className="px-8 py-4 text-lg font-medium text-center text-white bg-pink-600 rounded-md">
                <SignInButton>
                  Discover Your Meals Today →
                </SignInButton>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-center w-full lg:w-1/2">
          <div className="">
            <Image
              src={heroImg}
              width="500"
              height="501"
              className={"object-cover"}
              alt="Recipe Image"
              loading="eager"
              placeholder="blur"
            />
          </div>
        </div>
      </Container>
    </>
  );
}
