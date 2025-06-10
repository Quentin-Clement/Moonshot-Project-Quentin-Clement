import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, Download } from 'lucide-react';
import { useVideo } from '../context/VideoContext';
import VideoPlayer from '../components/VideoPlayer';
import VideoSegment from '../components/VideoSegment';

const BACKEND = 'https://liftguard-454389801374.europe-west9.run.app';

const ResultsPage: React.FC = () => {
  // grab the analyzed video and computed segments from context
  const { originalVideo, videoSegments } = useVideo();
  const navigate = useNavigate();

  // redirect back to home if no video is present
  useEffect(() => {
    if (!originalVideo) navigate('/');
  }, [originalVideo, navigate]);

  useEffect(() => {
    // DEBUG: log each segment’s correctness flags
    videoSegments.forEach(segment => {
      console.log(
        `Segment ${segment.segmentNumber}: ` +
        `depth_ok=${segment.depth_ok}, ` +
        `knees_ok=${segment.knees_ok}, ` +
        `toes_ok=${segment.toes_ok}`
      );
    });
  }, [videoSegments]);

  // Show a loading spinner while the backend processes the video
  if (!originalVideo) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        <p className="mt-4 text-sm text-slate-600">Analyzing your form...</p>
      </div>
    );
  }

  // Calculate the overall score and choose a color for it
  const correctCount = videoSegments.filter(s => s.isCorrect).length;
  const total = videoSegments.length;
  const percent = Math.round((correctCount / total) * 100);
  const scoreColor =
    percent >= 80
      ? 'text-green-600'
      : percent >= 60
      ? 'text-yellow-600'
      : 'text-red-600';

  // Main render
  return (
    <div className="space-y-6 px-4 max-w-lg mx-auto">
      {/* Header with back button and title */}
      <div className="flex items-center">
        <button
          onClick={() => navigate('/')} // go back to homepage
          className="mr-3 p-2 rounded-full bg-slate-100 active:bg-slate-200 transition-colors"
          aria-label="Go back"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-xl font-bold">Analysis Results</h1>
      </div>

      {/* Original Video Preview and Overall Score */}
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="p-4">
          <h2 className="text-lg font-semibold mb-3">Your Squat</h2>
          {/* play the original recorded squat */}
          <VideoPlayer
            src={`${BACKEND}${originalVideo.url}`}
            thumbnailUrl={`${BACKEND}${originalVideo.thumbnailUrl}`}
          />
        </div>
        <div className="border-t border-slate-100 p-4">
          <h3 className="font-medium mb-2">Overall Score</h3>
          <div className="flex items-baseline mb-4">
            {/* show percentage with dynamic color */}
            <span className={`text-3xl font-bold ${scoreColor}`}>{percent}%</span>
            <span className="ml-2 text-sm text-slate-600">
              {correctCount}/{total} correct
            </span>
          </div>
          {/* button to download or save results */}
          <button
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-full active:bg-blue-700 transition-colors text-sm font-medium"
          >
            <Download size={16} className="mr-2" />
            Save Analysis
          </button>
        </div>
      </div>

      {/* Detailed Breakdown Section: render each segment in a 3-column grid */}
      <div>
        <h2 className="text-lg font-semibold mb-2">Detailed Breakdown</h2>
        {/* grid-cols-3 creates three items per row; adjust at different breakpoints as needed */}
        <div className="grid grid-cols-3 md:grid-cols-6 lg:grid-cols-9 gap-4">
          {videoSegments.map((segment) => (
            // pass each segment to the VideoSegment component
            <VideoSegment key={segment.id} segment={segment}/>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResultsPage;
