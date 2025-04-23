import React from 'react';
import VideoUploader from '../components/VideoUploader';
import { ChevronDown } from 'lucide-react';

const HomePage: React.FC = () => {
  const scrollToUploader = () => {
    const uploaderSection = document.getElementById('uploader-section');
    if (uploaderSection) {
      uploaderSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="space-y-8 px-4 max-w-lg mx-auto">
      {/* Hero Section */}
      <section className="py-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 mb-4">
          <span className="text-blue-600">Perfect</span> Your Squat Form
        </h1>
        <p className="text-base text-slate-600 mb-6">
          Record or upload your squat and get instant AI feedback on your form.
        </p>
        <button 
          onClick={scrollToUploader}
          className="w-full max-w-xs px-6 py-3 bg-blue-600 text-white rounded-full text-lg font-medium active:bg-blue-700 transition-colors"
        >
          Start Analysis
        </button>
        <div className="mt-6 flex justify-center">
          <ChevronDown 
            size={24} 
            className="text-slate-400 animate-bounce cursor-pointer" 
            onClick={scrollToUploader}
          />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-8 bg-white rounded-2xl shadow-sm">
        <h2 className="text-xl font-bold text-center mb-8">How It Works</h2>
        <div className="space-y-6">
          <div className="px-6">
            <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-3 text-lg font-bold">1</div>
            <h3 className="text-lg font-semibold mb-2">Record or Upload</h3>
            <p className="text-slate-600 text-sm">Take a video of your squat or upload an existing one.</p>
          </div>
          <div className="px-6">
            <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-3 text-lg font-bold">2</div>
            <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
            <p className="text-slate-600 text-sm">Our AI breaks down your movement frame by frame.</p>
          </div>
          <div className="px-6">
            <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-3 text-lg font-bold">3</div>
            <h3 className="text-lg font-semibold mb-2">Get Feedback</h3>
            <p className="text-slate-600 text-sm">Receive detailed form feedback with visual guides.</p>
          </div>
        </div>
      </section>

      {/* Uploader Section */}
      <section id="uploader-section" className="py-8">
        <VideoUploader />
      </section>
    </div>
  );
};

export default HomePage;