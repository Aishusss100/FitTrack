import React, { useRef, useCallback } from "react";
import Webcam from "react-webcam";

const WebcamCapture = () => {
  const webcamRef = useRef(null);

  const videoConstraints = {
    facingMode: { exact: "environment" }, // Use rear camera on mobile
    width: 1280,
    height: 720
  };

  const capture = useCallback(() => {
    const currentWebcam = webcamRef.current; // Fixes ESLint warning
    if (currentWebcam) {
      const imageSrc = currentWebcam.getScreenshot();
      console.log(imageSrc);
    }
  }, []);

  return (
    <div>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        videoConstraints={videoConstraints}
      />
      <button onClick={capture}>Capture Photo</button>
    </div>
  );
};

export default WebcamCapture;
