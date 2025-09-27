'use client';
import { createContext, useContext, useRef, useState } from 'react';

const cameraContext = createContext();

export function CameraProvider({ children }) {
  const videoRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [stream, setStream] = useState(null);
  const [useExternal, setUseExternal] = useState(false);
  const [url, setUrl] = useState('');

  const startRecording = async () => {
    if (isRecording) return;
    if (useExternal && url) {
      console.log('Here');
      if (videoRef.current) {
        console.log('here');
        videoRef.current.srcObject = null;
        console.log(url);
        videoRef.current.src = url;
        videoRef.current.play();
      }
      setIsRecording(true);
      return;
    }

    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
      });
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        videoRef.current.play();
      }
      setIsRecording(true);
    } catch (err) {
      console.error('Error accessing camera:', err);
    }
  };
  const stopRecording = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.src = '';
    }
    setIsRecording(false);
    setUseExternal(false);
  };

  return (
    <cameraContext.Provider
      value={{
        isRecording,
        useExternal,
        url,
        setUseExternal,
        setUrl,
        videoRef,
        startRecording,
        stopRecording,
      }}
    >
      {children}
    </cameraContext.Provider>
  );
}

export function useCamera() {
  return useContext(cameraContext);
}
