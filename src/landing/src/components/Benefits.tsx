import Image from "next/image";
import React from "react";
import { Container } from "@/components/Container";

interface BenefitsProps {
  data: {
    bullets: {
      title: string;
      desc: string;
      icon: React.ReactNode;
    }[];
  };
}

export const Benefits = (props: Readonly<BenefitsProps>) => {
  const { data } = props;

  return (
    <Container className="flex flex-wrap mb-20 lg:gap-10">
      <div className="flex justify-between w-full">
        <div className="w-full">
          <div className="flex flex-wrap lg:flex-nowrap">
            {data.bullets.map((item, index) => (
              <div key={index} className="bg-white shadow-lg rounded-lg p-5 m-2 w-full lg:w-1/4">
                <div className="flex flex-col h-full">
                  <div className="flex items-center justify-center bg-pink-500 rounded-md w-11 h-11 mb-3">
                    <span className="w-7 h-7 text-pink-50">
                      {React.isValidElement(item.icon) ? item.icon : null}
                    </span>
                  </div>
                  <h4 className="text-xl font-medium text-gray-800 dark:text-gray-200 mb-2">
                    {item.title}
                  </h4>
                  <p className="text-gray-500 dark:text-gray-400 flex-grow">
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Container>
  );
};
