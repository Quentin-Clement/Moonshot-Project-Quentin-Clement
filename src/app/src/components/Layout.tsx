import React from 'react';
import { Dumbbell } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const isHomePage = location.pathname === '/';

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <header className="bg-white shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="px-4 py-3 flex justify-between items-center max-w-lg mx-auto">
          <Link to="/" className="flex items-center space-x-2 text-blue-600">
            <Dumbbell size={24} />
            <span className="text-lg font-bold">LiftGuard</span>
          </Link>
          {!isHomePage && (
            <Link 
              to="/" 
              className="px-3 py-1.5 text-sm rounded-full bg-blue-600 text-white active:bg-blue-700 transition-colors"
            >
              New Analysis
            </Link>
          )}
        </div>
      </header>
      
      <main className="flex-grow pt-14 pb-16">
        {children}
      </main>
      
      <footer className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 py-2 px-4 text-center text-xs text-slate-500">
        <p>© {new Date().getFullYear()}  Analyzer</p>
      </footer>
    </div>
  );
};

export default Layout;