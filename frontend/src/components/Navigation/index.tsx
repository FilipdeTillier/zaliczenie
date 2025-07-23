import { CHAT, MAIN } from "../../../router/appPaths";
import { Link, useLocation } from "react-router-dom";

import { useState } from "react";

const NAV_LINKS = [
  { name: "Home", path: `/${MAIN}` },
  { name: "Chat", path: CHAT },
];

export const Navigation = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();

  // iPhone 13 width is 390px, so we'll use 'sm' (640px) as breakpoint for simplicity
  return (
    <nav className="w-full bg-white shadow-md fixed top-0 left-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo mock */}
          <div className="flex-shrink-0 flex items-center">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center font-bold text-lg text-gray-600">
              LOGO
            </div>
          </div>
          {/* Desktop links */}
          <div className="hidden sm:flex flex-1 items-center justify-end space-x-8">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className={`px-4 py-2 rounded transition-colors duration-200 flex items-center
                  ${
                    location.pathname === link.path
                      ? "text-gray-900 font-semibold"
                      : "text-gray-700"
                  }
                  hover:bg-gray-100 hover:text-gray-500
                `}
              >
                {link.name}
              </Link>
            ))}
          </div>
          {/* Burger button for mobile */}
          <div className="sm:hidden flex items-center">
            <button
              onClick={() => setMenuOpen((open) => !open)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
              aria-label="Open main menu"
            >
              <svg
                className="h-6 w-6"
                stroke="currentColor"
                fill="none"
                viewBox="0 0 24 24"
              >
                {menuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>
      {/* Mobile menu */}
      {menuOpen && (
        <div className="sm:hidden fixed inset-0 bg-white bg-opacity-95 flex flex-col items-center justify-center z-40">
          <button
            onClick={() => setMenuOpen(false)}
            className="absolute top-4 right-4 p-2 rounded-md text-gray-700 hover:text-gray-900 hover:bg-gray-100 focus:outline-none"
            aria-label="Close menu"
          >
            <svg
              className="h-6 w-6"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <div className="flex flex-col space-y-8 mt-8">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                onClick={() => setMenuOpen(false)}
                className={`text-2xl px-6 py-3 rounded transition-colors duration-200 text-center
                  ${
                    location.pathname === link.path
                      ? "text-gray-900 font-semibold"
                      : "text-gray-700"
                  }
                  hover:bg-gray-100 hover:text-gray-500
                `}
              >
                {link.name}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  );
};
