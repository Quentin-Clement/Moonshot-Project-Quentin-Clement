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
  
  depth_ok: boolean;
  knees_ok: boolean;
  toes_ok: boolean;
}