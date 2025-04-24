import React, { createContext, useState, useContext } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { VideoData, VideoSegment } from '../types';

interface VideoContextType {
  originalVideo: VideoData | null;
  videoSegments: VideoSegment[];
  setOriginalVideo: (video: VideoData) => void;
  processVideo: (videoFile: File) => Promise<void>;
  clearVideos: () => void;
}

const VideoContext = createContext<VideoContextType | undefined>(undefined);

export const VideoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [originalVideo, setOriginalVideo] = useState<VideoData | null>(null);
  const [videoSegments, setVideoSegments] = useState<VideoSegment[]>([]);

  // This function simulates processing by a backend
  // In a real app, this would send the video to a backend service
  const processVideo = async (videoFile: File): Promise<void> => {
    // Create URL for the original video
    const videoUrl = URL.createObjectURL(videoFile);
    
    // Set the original video data
    const newOriginalVideo: VideoData = {
      id: uuidv4(),
      name: videoFile.name,
      url: videoUrl,
      thumbnailUrl: videoUrl, // In a real app, we'd generate a thumbnail
      duration: 0, // In a real app, we'd calculate this
      createdAt: new Date().toISOString(),
    };
    
    setOriginalVideo(newOriginalVideo);
    
    // Simulate creating 5 video segments with random correctness status
    // In a real app, these would be created by the backend
    // Send to backend for real processing
    const form = new FormData();
    form.append('video', videoFile);

    try {
      const res = await fetch('/api/process-video', {
        method: 'POST',
        body: form,
      });
      if (!res.ok) {
        const err = await res.text();
        throw new Error(err || res.statusText);
      }
      const data = await res.json();

      // originalVideo comes with { url, thumbnailUrl }
      setOriginalVideo({
        id: uuidv4(),
        ...data.originalVideo,
      });

      // videoSegments is an array of { id, segmentNumber, url, thumbnailUrl, startTime, endTime }
      setVideoSegments(data.videoSegments);
    } catch (e) {
      console.error('Video processing failed:', e);
      throw e;
    }
  };

  const clearVideos = () => {
    if (originalVideo) {
      URL.revokeObjectURL(originalVideo.url);
    }
    
    videoSegments.forEach(segment => {
      // Only revoke if it's a different URL than the original
      if (segment.url !== originalVideo?.url) {
        URL.revokeObjectURL(segment.url);
      }
    });
    
    setOriginalVideo(null);
    setVideoSegments([]);
  };

  return (
    <VideoContext.Provider 
      value={{ 
        originalVideo, 
        videoSegments, 
        setOriginalVideo, 
        processVideo,
        clearVideos
      }}
    >
      {children}
    </VideoContext.Provider>
  );
};

export const useVideo = (): VideoContextType => {
  const context = useContext(VideoContext);
  if (context === undefined) {
    throw new Error('useVideo must be used within a VideoProvider');
  }
  return context;
};