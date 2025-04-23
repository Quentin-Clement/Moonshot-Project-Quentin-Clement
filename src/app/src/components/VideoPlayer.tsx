// components/VideoPlayer.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Play, Pause, Volume2, VolumeX, RotateCcw } from 'lucide-react';

interface VideoPlayerProps {
  src: string;
  autoPlay?: boolean;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  src,
  autoPlay = false,
}) => {
  const [isPlaying, setIsPlaying] = useState(autoPlay);
  const [isMuted, setIsMuted] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [controlsVisible, setControlsVisible] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const controlsTimeout = useRef<number>();

  // play/pause
  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    if (isPlaying) {
      v.play().catch(() => setIsPlaying(false));
    } else {
      v.pause();
    }
  }, [isPlaying]);

  // mute
  useEffect(() => {
    if (videoRef.current) videoRef.current.muted = isMuted;
  }, [isMuted]);

  const showCtrls = () => {
    setControlsVisible(true);
    window.clearTimeout(controlsTimeout.current);
    controlsTimeout.current = window.setTimeout(() => {
      setControlsVisible(false);
    }, 3000);
  };

  const onLoadedMeta = () => {
    const v = videoRef.current;
    if (!v) return;
    setDuration(v.duration);

    // ensure we're paused on the very first frame...
    v.currentTime = 0;
    v.pause();

    // remove any poster so the real frame shows
    v.removeAttribute('poster');
  };

  const onTimeUpdate = () => {
    if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
  };

  const format = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="relative touch-none" onTouchStart={showCtrls}>
      <video
        ref={videoRef}
        src={src}
        preload="metadata"
        playsInline
        className="w-full h-auto"
        onLoadedMetadata={onLoadedMeta}
        onTimeUpdate={onTimeUpdate}
        onEnded={() => setIsPlaying(false)}
        onClick={() => setIsPlaying(p => !p)}
      />

      {/* dark overlay */}
      <div
        className={`absolute inset-0 bg-black/40 transition-opacity duration-300 ${
          controlsVisible ? 'opacity-100' : 'opacity-0'
        }`}
      />

      {/* controls */}
      <div
        className={`absolute bottom-0 left-0 right-0 p-3 transition-opacity duration-300 ${
          controlsVisible ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <div className="flex items-center gap-2 mb-1">
          <button
            onClick={e => {
              e.stopPropagation();
              setIsPlaying(p => !p);
            }}
            className="text-white active:text-blue-400 transition-colors"
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} />}
          </button>

          <button
            onClick={e => {
              e.stopPropagation();
              setIsMuted(m => !m);
            }}
            className="text-white active:text-blue-400 transition-colors"
          >
            {isMuted ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>

          <button
            onClick={e => {
              e.stopPropagation();
              if (videoRef.current) {
                videoRef.current.currentTime = 0;
                setCurrentTime(0);
                setIsPlaying(true);
              }
            }}
            className="text-white active:text-blue-400 transition-colors"
          >
            <RotateCcw size={18} />
          </button>

          <span className="text-white text-xs ml-1">
            {format(currentTime)} / {format(duration)}
          </span>
        </div>

        <input
          type="range"
          min={0}
          max={duration}
          value={currentTime}
          onChange={e => {
            const t = parseFloat(e.currentTarget.value);
            if (videoRef.current) videoRef.current.currentTime = t;
            setCurrentTime(t);
          }}
          onClick={e => e.stopPropagation()}
          className="w-full h-1 bg-white/30 rounded-full appearance-none touch-none"
        />
      </div>
    </div>
  );
};

export default VideoPlayer;