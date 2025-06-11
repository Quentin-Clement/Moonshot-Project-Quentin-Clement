import React from 'react';
import { Link } from 'react-router-dom';
import { VideoSegment as VideoSegmentType } from '../types';

// Backend URL defined in .env file
const BACKEND = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:8000';

interface VideoSegmentProps {
  segment: VideoSegmentType;
}

export default function VideoSegment({ segment }: VideoSegmentProps) {
  const { id, thumbnailUrl, isCorrect } = segment;
  const badgeClasses = isCorrect
    ? 'bg-green-500 text-white'
    : 'bg-red-500 text-white';

  return (
    <Link to={`/segment/${id}`} className="block">
      <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
        <div className="relative">
          <img
            src={`${BACKEND}${thumbnailUrl}`}
            alt={`Segment ${id}`}
            className="w-full h-auto"
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
      </div>
    </Link>
  );
}
