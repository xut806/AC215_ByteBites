import React from "react";
import { Container } from "@/components/Container";

interface SectionTitleProps {
  preTitle?: string;
  title?: React.ReactNode;
  align?: "left" | "center";
  children?: React.ReactNode;
}

export const SectionTitle = (props: Readonly<SectionTitleProps>) => {
  return (
    <Container
      className={`flex w-full flex-col mt-4 ${
        props.align === "left" ? "" : "items-center justify-center text-center"
      }`}>
      {props.preTitle && (
        <div className="bg-pink-50 rounded-full px-4 py-2">
          <h2 className="text-sm font-bold tracking-wider text-pink-600">
            {props.preTitle}
          </h2>
        </div> 
      )}

      {props.title && (
        <h2 className="max-w-2xl mt-3 text-3xl font-bold leading-snug tracking-tight text-gray-800 lg:leading-tight lg:text-4xl dark:text-white">
          {props.title}
        </h2>
      )}

      {props.children && (
        <p className="max-w-2xl py-4 text-base leading-normal text-gray-500 lg:text-lg xl:text-lg dark:text-gray-300">
          {props.children}
        </p>
      )}
    </Container>
  );
}

