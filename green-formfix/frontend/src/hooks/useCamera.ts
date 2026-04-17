// src/hooks/useCamera.ts
import { useRef, useState, useEffect } from "react";
export const useCamera = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function setupCamera() {
      // Check if mediaDevices exists (it won't on insecure HTTP)
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera API not available. Use HTTPS or localhost.");
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: true, 
          audio: false 
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setIsActive(true);
        }
      } catch (err) {
        setError("Camera access denied.");
      }
    }
    setupCamera();

    return () => {
      const stream = videoRef.current?.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
    };
  }, []);

  return { videoRef, isActive, error };
};