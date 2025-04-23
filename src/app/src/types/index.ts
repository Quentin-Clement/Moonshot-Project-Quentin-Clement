export interface VideoData {
  id: string;
  name: string;
  url: string;
  thumbnailUrl: string;
  duration: number;
  createdAt: string;
}

export interface VideoSegment {
  id: string;
  originalVideoId: string;
  segmentNumber: number;
  url: string;
  thumbnailUrl: string;
  isCorrect: boolean;
  feedback: string;
  duration: number;
}