import React, { useState, useRef, useEffect } from 'react';
import { Upload, Camera, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useVideo } from '../context/VideoContext';
import { Capacitor } from '@capacitor/core';

declare global {
  interface Navigator {
    device?: {
      capture: {
        captureVideo: (
          success: (mediaFiles: any[]) => void,
          error: (err: any) => void,
          options?: any
        ) => void;
      };
    };
  }
}

const isNative = Capacitor.getPlatform() !== 'web';

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

  // For web: assign stream to video after mount
  useEffect(() => {
    if (!isNative && isRecording && recordingStream && videoRef.current) {
      videoRef.current.srcObject = recordingStream;
      videoRef.current
        .play()
        .catch(() => { /* ignore autoplay errors */ });
    }
  }, [isRecording, recordingStream]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.includes('video')) {
        await handleVideoProcessing(file);
      } else {
        alert('Please upload a video file');
      }
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      await handleVideoProcessing(e.target.files[0]);
    }
  };

  const handleVideoProcessing = async (file: File) => {
    try {
      setIsProcessing(true);
      await processVideo(file);
      navigate('/results');
    } catch (err) {
      console.error('Error processing video:', err);
      alert('There was an error processing your video');
    } finally {
      setIsProcessing(false);
      setIsRecording(false);
    }
  };

  const startRecording = async () => {
    if (isNative && navigator.device?.capture) {
      // Native capture via Cordova MediaCapture plugin
      const options = { limit: 1, duration: 60 };
      navigator.device.capture.captureVideo(
        async (mediaFiles: any[]) => {
          const mf = mediaFiles[0];
          const nativePath = mf.fullPath || mf.localURL;
          try {
            const uri = nativePath.startsWith('file://')
              ? nativePath
              : `file://${nativePath}`;
            const response = await fetch(uri);
            const blob = await response.blob();
            const file = new File([blob], mf.name, { type: mf.type });
            await handleVideoProcessing(file);
          } catch (err) {
            console.error('Error reading recorded file', err);
            alert('Error processing recorded video');
          }
        },
        (err: any) => {
          console.error('Capture error:', err);
          alert('Could not record video');
        },
        options
      );
    } else {
      // Web fallback using getUserMedia + MediaRecorder
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: false,
        });
        setRecordingStream(stream);
        setIsRecording(true);

        const recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);
        const chunks: BlobPart[] = [];
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0) chunks.push(e.data);
        };
        recorder.onstop = async () => {
          const blob = new Blob(chunks, { type: 'video/mp4' });
          const file = new File([blob], 'recorded-squat.mp4', { type: 'video/mp4' });
          await handleVideoProcessing(file);
        };
        recorder.start();
      } catch (err) {
        console.error('Error starting recording:', err);
        alert('Could not access camera. Please check permissions.');
      }
    }
  };

  const stopRecording = () => {
    if (!isNative) {
      mediaRecorder?.stop();
      recordingStream?.getTracks().forEach((t) => t.stop());
      setRecordingStream(null);
      if (videoRef.current) videoRef.current.srcObject = null;
      setIsRecording(false);
    }
    // For native, capture UI closes automatically
  };

  return (
    <div className="w-full">
      {!isRecording || isNative ? (
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
            <p className="mt-2 text-sm text-slate-600">Tap to upload or drop a video here</p>

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
            className="w-full h-auto"
            webkit-playsinline="true"
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