import Image from "next/image";
import React from "react";
import { Container } from "@/components/Container";

import userOneImg from "../../public/img/user1.jpg";
import userTwoImg from "../../public/img/user2.jpg";

export const Testimonials = () => {
  return (
    <Container>
      <div className="flex flex-col gap-10 items-center">
        {/* First Testimonial */}
        <div className="flex flex-col justify-between w-3/4 h-full bg-gray-100 px-10 rounded-2xl py-10 dark:bg-trueGray-800">
          <div className="flex items-center">
            <div className="flex-shrink-0 overflow-hidden rounded-full w-14 h-14">
              <Image
                src={userOneImg}
                width="40"
                height="40"
                alt="Avatar"
                placeholder="blur"
              />
            </div>
            <div className="ml-3">
              {/* Star Rating */}
              <p className="text-lg font-medium">Yilin Qi</p>
              <p className="text-gray-600 dark:text-gray-400">Harvard Student</p>
              <span className="text-yellow-500">★★★★★</span>
            </div>
          </div>
          <div className="flex items-center mt-2">
          </div>
          <p className="mt-4 text-base">
            &quot;Thanks to ByteBites, meal prep has never been easier! It turns my grocery receipts into personalized, healthy recipes in seconds, saving me time and reducing food waste. A total game-changer for my busy schedule!&quot;
          </p>
        </div>

        {/* Second Testimonial */}
        <div className="flex flex-col justify-between w-3/4 h-full bg-gray-100 px-10 rounded-2xl py-10 dark:bg-trueGray-800">
          <div className="flex items-center">
            <div className="flex-shrink-0 overflow-hidden rounded-full w-14 h-14">
              <Image
                src={userTwoImg}
                width="40"
                height="40"
                alt="Avatar"
                placeholder="blur"
              />
            </div>
            <div className="ml-3">
              <p className="text-lg font-medium">Victoria Tang</p>
              <p className="text-gray-600 dark:text-gray-400">Harvard Student</p>
              <span className="text-yellow-500">★★★★★</span>
            </div>
          </div>
          <div className="flex items-center mt-2">
          </div>
          <p className="mt-4 text-base">
            &quot;ByteBites has completely transformed how I plan my meals! With its personalized recipes and nutrition insights, I&#39;m eating smarter and wasting less food. It&#39;s the perfect app for effortless, healthier and smarter cooking!&quot;
          </p>
        </div>
      </div>
    </Container>
  );
};
