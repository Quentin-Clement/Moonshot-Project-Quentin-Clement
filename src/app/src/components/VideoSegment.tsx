import React from 'react';
import { Link } from 'react-router-dom';
import { VideoSegment as VideoSegmentType } from '../types';
import VideoPlayer from './VideoPlayer';

interface VideoSegmentProps {
  segment: VideoSegmentType;
}

const VideoSegment: React.FC<VideoSegmentProps> = ({ segment }) => {
  return (
    <Link to={`/segment/${segment.id}`} className="block">
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden active:opacity-90 transitiƒ-opacity">
        <div className="relative">
          <VideoPlayer
            src={segment.url}
            thumbnailUrl={segment.thumbnailUrl}
            autoPlay={false}
          />
          <span className="absolute top-2 left-2 bg-slate-800 text-white text-xs font-semibold px-2 py-1 rounded-full">
            {segment.segmentNumber}
          </span>
          <span className={`absolute bottom-2 right-2 ${
            segment.isCorrect 
              ? 'bg-green-500' 
              : 'bg-red-500'
          } text-white px-2 py-0.5 rounded-md z-10 text-xs font-medium`}>
            {segment.isCorrect ? 'Correct' : 'Incorrect'}
          </span>
        </div>
        
        <div className="p-4">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-base font-semibold">Phase {segment.segmentNumber}</h3>
          </div>
          <p className="text-sm text-slate-600 line-clamp-2">
            {segment.feedback}
          </p>
        </div>
      </div>
    </Link>
  );
};

export default VideoSegment;