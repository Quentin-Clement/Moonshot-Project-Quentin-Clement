import React from 'react';
import { VideoSegment as VideoSegmentType } from '../types';
import VideoPlayer from './VideoPlayer';

interface VideoSegmentProps {
  segment: VideoSegmentType;
}

const VideoSegment: React.FC<VideoSegmentProps> = ({ segment }) => {
  const statusColor = segment.isCorrect === undefined 
    ? 'transparent' 
    : segment.isCorrect 
      ? 'bg-green-500' 
      : 'bg-red-500';

  return (
    <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
      {/* container for video and badges */}
      <div className="relative">
        <VideoPlayer
          src={segment.url}
          thumbnailUrl={segment.thumbnailUrl}
          // Don't pass isCorrect anymore since we're handling it here
        />
        {/* badge at top-left showing segment number */}
        <span className="absolute top-2 left-2 bg-slate-800 text-white text-xs font-semibold px-2 py-1 rounded-full">
          {segment.segmentNumber}
        </span>
        {/* badge at bottom-right showing correctness */}
        {segment.isCorrect !== undefined && (
          <span
            className={`absolute bottom-2 right-2 ${statusColor} text-white px-2 py-0.5 rounded-md z-10 text-xs font-medium`}>
            {segment.isCorrect ? 'Correct' : 'Incorrect'}
          </span>
        )}
      </div>
    </div>
  );
};

export default VideoSegment;