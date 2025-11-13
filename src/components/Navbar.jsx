import React, { useState } from 'react';
import { Menu, X } from 'lucide-react';
export default Navbar;

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="bg-white shadow-sm fixed w-full top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <span className="text-2xl font-bold text-indigo-600">HackProject</span>
          </div>
          
          <div className="hidden md:flex items-center space-x-8">
            <a href="#home" className="text-gray-700 hover:text-indigo-600 transition">Home</a>
            <a href="#features" className="text-gray-700 hover:text-indigo-600 transition">Features</a>
            <a href="#about" className="text-gray-700 hover:text-indigo-600 transition">About</a>
            <a href="#contact" className="text-gray-700 hover:text-indigo-600 transition">Contact</a>
            <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition">
              Get Started
            </button>
          </div>

          <div className="md:hidden flex items-center">
            <button onClick={() => setIsOpen(!isOpen)} className="text-gray-700">
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden bg-white border-t">
          <div className="px-2 pt-2 pb-3 space-y-1">
            <a href="#home" className="block px-3 py-2 text-gray-700 hover:bg-indigo-50 rounded">Home</a>
            <a href="#features" className="block px-3 py-2 text-gray-700 hover:bg-indigo-50 rounded">Features</a>
            <a href="#about" className="block px-3 py-2 text-gray-700 hover:bg-indigo-50 rounded">About</a>
            <a href="#contact" className="block px-3 py-2 text-gray-700 hover:bg-indigo-50 rounded">Contact</a>
            <button className="w-full text-left px-3 py-2 bg-indigo-600 text-white rounded mt-2">
              Get Started
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};