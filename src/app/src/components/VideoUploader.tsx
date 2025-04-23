import React, { useState, useRef } from 'react';
import { Upload, Camera, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';

const VideoUploader: React.FC = () => {
  const { processVideo } = useVideo();
  const navigate = useNavigate();
  const [isDragging, setIsDragging] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recordingStream, setRecordingStream] = useState<MediaStream | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };
  
  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.includes('video')) {
        await handleVideoProcessing(file);
      } else {
        alert('Please upload a video file');
      }
    }
  };
  
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await handleVideoProcessing(file);
    }
  };
  
  const handleVideoProcessing = async (file: File) => {
    try {
      setIsProcessing(true);
      await processVideo(file);
      navigate('/results');
    } catch (error) {
      console.error('Error processing video:', error);
      alert('There was an error processing your video');
    } finally {
      setIsProcessing(false);
    }
  };
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'environment' }, 
        audio: false 
      });
      setRecordingStream(stream);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      
      const chunks: BlobPart[] = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };
      
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'video/mp4' });
        const file = new File([blob], 'recorded-squat.mp4', { type: 'video/mp4' });
        await handleVideoProcessing(file);
      };
      
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      alert('Could not access camera. Please check permissions.');
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
    
    if (recordingStream) {
      recordingStream.getTracks().forEach(track => track.stop());
      setRecordingStream(null);
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  };
  
  return (
    <div className="w-full">
      {!isRecording ? (
        <div className="space-y-4">
          <button
            onClick={startRecording}
            className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-full active:bg-blue-700 transition-colors text-lg font-medium"
            disabled={isProcessing}
          >
            <Camera className="mr-2 h-5 w-5" />
            Record Squat
          </button>
          
          <div 
            className={`border-2 border-dashed rounded-2xl p-6 text-center transition-colors ${
              isDragging ? 'border-blue-600 bg-blue-50' : 'border-slate-200'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleFileDrop}
          >
            <Upload className="mx-auto h-8 w-8 text-slate-400" />
            <p className="mt-2 text-sm text-slate-600">
              Tap to upload or drop a video here
            </p>
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="mt-4 px-4 py-2 text-sm text-blue-600 border border-blue-600 rounded-full active:bg-blue-50 transition-colors"
              disabled={isProcessing}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 inline animate-spin" />
                  Processing...
                </>
              ) : (
                'Choose Video'
              )}
            </button>
            
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              capture="environment"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm overflow-hidden">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline
            muted 
            className="w-full h-auto bg-black"
          />
          <div className="p-4">
            <button
              type="button"
              onClick={stopRecording}
              className="w-full px-4 py-2 bg-red-600 text-white rounded-full active:bg-red-700 transition-colors text-lg font-medium"
            >
              Stop Recording
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;