import React from 'react';
import { ArrowRight } from 'lucide-react';
export default Hero;

const Hero = () => {
  return (
    <section id="home" className="pt-24 pb-16 bg-gradient-to-br from-indigo-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Build Something
            <span className="text-indigo-600"> Amazing</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            A fullstack solution that transforms the way you work. Fast, reliable, and built for the modern web.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition flex items-center justify-center">
              Get Started <ArrowRight className="ml-2" size={20} />
            </button>
            <button className="border-2 border-indigo-600 text-indigo-600 px-8 py-3 rounded-lg hover:bg-indigo-50 transition">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </section>
  );
};