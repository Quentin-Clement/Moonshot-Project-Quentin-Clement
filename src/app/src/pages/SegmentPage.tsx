import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, XCircle } from 'lucide-react';
import { useVideo } from '../context/VideoContext';
import VideoPlayer from '../components/VideoPlayer';

// Backend URL defined in .env file
const BACKEND = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';

const SegmentPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { videoSegments } = useVideo();

  const segment = videoSegments.find(s => s.id === id);

  if (!segment) {
    return (
      <div className="p-4">
        <p className="text-center text-slate-600">Segment not found</p>
      </div>
    );
  }

  const Parameter: React.FC<{
    label: string;
    isCorrect: boolean;
    description: string;
  }> = ({ label, isCorrect, description }) => (
    <div className="flex items-start space-x-3 p-4 bg-slate-50 rounded-xl">
      {isCorrect ? (
        <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0" />
      ) : (
        <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
      )}
      <div>
        <h3 className="font-medium text-slate-900">{label}</h3>
        <p className="text-sm text-slate-600 mt-1">{description}</p>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 px-4 max-w-lg mx-auto pb-8">
      <div className="flex items-center">
        <button
          onClick={() => navigate('/results')}
          className="mr-3 p-2 rounded-full bg-slate-100 active:bg-slate-200 transition-colors"
          aria-label="Go back"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="text-xl font-bold">Phase {segment.segmentNumber} Analysis</h1>
      </div>

      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <VideoPlayer
          src={`${BACKEND}${segment.url}`}
          thumbnailUrl={segment.thumbnailUrl}
          autoPlay={false}
        />
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold px-1">Form Analysis</h2>

        <Parameter
          label="Squat Depth"
          isCorrect={segment.depth_ok}
          description={
            segment.depth_ok
              ? "Good depth achieved. Your hips go below parallel with your knees."
              : "Insufficient depth. Try to lower your hips below parallel with your knees."
          }
        />

        <Parameter
          label="Knee Alignment"
          isCorrect={segment.knees_ok}
          description={
            segment.knees_ok
              ? "Excellent knee tracking. Your knees stay in line with your toes."
              : "Knees are caving inward. Focus on pushing them outward in line with your toes."
          }
        />

        <Parameter
          label="Foot Position"
          isCorrect={segment.toes_ok}
          description={
            segment.toes_ok
              ? "Great foot positioning. Weight is distributed properly."
              : "Check your foot position. Ensure your weight is evenly distributed."
          }
        />
      </div>

      <div className="bg-white rounded-2xl shadow-sm p-4">
        <h2 className="text-lg font-semibold mb-3">AI Feedback</h2>
        <div className="prose prose-sm text-slate-600">
          <p className="text-sm leading-relaxed">
            {segment.tips}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SegmentPage;