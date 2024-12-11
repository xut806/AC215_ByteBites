import {
  FaceSmileIcon,
  ChartBarSquareIcon,
  CursorArrowRaysIcon,
  DevicePhoneMobileIcon,
} from "@heroicons/react/24/solid";

import Imgone from "../../public/img/steps/step1.png"; 
import Imgtwo from "../../public/img/steps/step2.png"; 
import Imgthree from "../../public/img/steps/step3.png"; 
import Image from "next/image";

export const benefitOne = {
  bullets: [
    {
      title: "Automated Ingredient Recognition",
      desc: "Use the OCR model to identify ingredients directly from grocery receipts.",
      icon: <FaceSmileIcon />,
    },
    {
      title: "Personalized Meal Planning",
      desc: "Generate recipes tailored to dietary restrictions, time constraints, and meal types.",
      icon: <ChartBarSquareIcon />,
    },
    {
      title: "Health and Wellness Integration",
      desc: "Track nutrient intake and gain personalized insights to improve your diet.",
      icon: <CursorArrowRaysIcon />,
    },
    {
      title: "User-Driven Recipe Refinement",
      desc: "Enhance recipe recommendations through user feedback and RLHF optimization.",
      icon: <DevicePhoneMobileIcon />,
    }
  ],
};

export const steps = {
  items: [
      {
        title: "Upload your grocery receipt",
        description: "We extract and identify the ingredients from your receipt to create personalized recipe ingredient lists.",
        image: <Image src={Imgone} alt="step1" />,
      },
      {
        title: "Set your dietary preferences",
        description: "Choose from a variety of dietary restrictions, meal types, and time constraints to customize your meals.",
        image: <Image src={Imgtwo} alt="step2" />,
      },
      {
        title: "Get recipes & nutrition analysis",
        description: "Receive tailored recipes based on your preferences and ingredients, complete with detailed nutritional information.",
        image: <Image src={Imgthree} alt="step3" />,
      },      
  ],
};
