// src/hooks/useCamera.ts
import { useRef, useState, useEffect } from "react";
export const useCamera = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const video = videoRef.current;

    async function setupCamera() {
      // Check if mediaDevices exists (it won't on insecure HTTP)
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera needs HTTPS or http://localhost. Open the app from localhost.");
        return;
      }

      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false,
        });
        if (video) {
          video.srcObject = stream;
          await video.play();
          setIsActive(true);
        }
      } catch (err) {
        const errorName = err instanceof DOMException ? err.name : "";
        if (errorName === "NotAllowedError" || errorName === "PermissionDeniedError") {
          setError("Camera access is blocked. Allow camera permission in your browser and reload.");
        } else if (errorName === "NotFoundError") {
          setError("No camera was found. Connect a camera and reload.");
        } else if (errorName === "NotReadableError") {
          setError("Camera is being used by another app. Close it and reload.");
        } else {
          setError("Unable to start the camera. Use HTTPS or open the app from localhost.");
        }
      }
    }
    setupCamera();

    return () => {
      const stream = video?.srcObject as MediaStream;
      stream?.getTracks().forEach(track => track.stop());
    };
  }, []);

  return { videoRef, isActive, error };
};
