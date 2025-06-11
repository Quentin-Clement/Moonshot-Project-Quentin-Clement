import React, { createContext, useState, useContext } from 'react';
import { VideoData, VideoSegment } from '../types';

// Backend base URL
const BACKEND = 'https://liftguard-454389801374.europe-west9.run.app';

interface VideoContextType {
  originalVideo: VideoData | null;
  videoSegments: VideoSegment[];
  processVideo: (videoFile: File) => Promise<void>;
  clearVideos: () => void;
}

const VideoContext = createContext<VideoContextType | undefined>(undefined);

export const VideoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [originalVideo, setOriginalVideo] = useState<VideoData | null>(null);
  const [videoSegments, setVideoSegments] = useState<VideoSegment[]>([]);

  // Send the video file to the backend for processing
  const processVideo = async (videoFile: File): Promise<void> => {
    const form = new FormData();
    form.append('video', videoFile);

    try {
      const res = await fetch(`${BACKEND}/api/process-video`, {
        method: 'POST',
        body: form,
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || res.statusText);
      }

      const data: {
        originalVideo: VideoData;
        videoSegments: VideoSegment[];
      } = await res.json();

      setOriginalVideo(data.originalVideo);
      setVideoSegments(data.videoSegments);
    } catch (e) {
      console.error('Error processing video:', e);
      throw e;
    }
  };

  const clearVideos = () => {
    setOriginalVideo(null);
    setVideoSegments([]);
  };

  return (
    <VideoContext.Provider value={{ originalVideo, videoSegments, processVideo, clearVideos }}>
      {children}
    </VideoContext.Provider>
  );
};

export const useVideo = (): VideoContextType => {
  const context = useContext(VideoContext);
  if (!context) {
    throw new Error('useVideo must be used within a VideoProvider');
  }
  return context;
};
