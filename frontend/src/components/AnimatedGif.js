import React from 'react';

const AnimatedGif = ({ src, alt, className = "", width = "auto", height = "auto" }) => {
  return (
    <div className={`animated-gif-container ${className}`}>
      <img 
        src={src} 
        alt={alt} 
        width={width} 
        height={height}
        className="animated-gif"
        loading="lazy"
      />
    </div>
  );
};

export default AnimatedGif; 