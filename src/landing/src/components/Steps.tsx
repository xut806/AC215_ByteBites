import React from 'react';
import { steps } from './data';

const Steps = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {steps.items.map((step, index) => (
        <div key={index} className="p-4 border rounded-lg shadow-md relative">
          <span className="absolute top-2 left-2 w-8 h-8 flex items-center justify-center bg-pink-500 text-white rounded-full font-bold">
            {index + 1}
          </span>
          {step.image}
          <h3 className="text-lg font-semibold mt-2">{step.title}</h3>
          <p className="mt-2">{step.description}</p>
        </div>
      ))}
    </div>
  );
};

export default Steps;
