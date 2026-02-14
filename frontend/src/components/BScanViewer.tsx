/**
 * B-scan viewer component with hover magnifier.
 * Shows a smaller preview with a magnifying lens on hover.
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { Label, LabelNames } from '@/types';
import styles from './BScanViewer.module.css';

interface BScanViewerProps {
  previewUrl: string;
  label: Label;
  bscanIndex: number;
  isLoading?: boolean;
  maxWidth: number;
  onMaxWidthChange: (width: number) => void;
}

const MAGNIFIER_SIZE = 200;
const ZOOM_LEVEL = 2.5;
const MIN_WIDTH = 300;
const MAX_WIDTH = 900;
const STEP = 50;

function BScanViewer({
  previewUrl,
  label,
  bscanIndex,
  isLoading = false,
  maxWidth,
  onMaxWidthChange,
}: BScanViewerProps) {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(previewUrl);
  const [showMagnifier, setShowMagnifier] = useState(false);

  // Reset imageLoaded when the image URL changes
  useEffect(() => {
    if (previewUrl !== currentSrc) {
      setImageLoaded(false);
      setCurrentSrc(previewUrl);
    }
  }, [previewUrl, currentSrc]);
  const [magnifierPos, setMagnifierPos] = useState({ x: 0, y: 0 });
  const imgRef = useRef<HTMLImageElement>(null);

  const getLabelClass = () => {
    switch (label) {
      case Label.Healthy:
        return styles.labelHealthy;
      case Label.Unhealthy:
        return styles.labelUnhealthy;
      default:
        return styles.labelUnlabeled;
    }
  };

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const img = imgRef.current;
    if (!img) return;

    const rect = img.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    setMagnifierPos({ x, y });
  }, []);

  const handleMouseEnter = useCallback(() => {
    setShowMagnifier(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setShowMagnifier(false);
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.index}>B-scan #{bscanIndex}</span>
        <span className={`${styles.labelBadge} ${getLabelClass()}`}>
          {LabelNames[label]}
        </span>
      </div>

      <div className={styles.sizeControl}>
        <button
          className={styles.sizeBtn}
          onClick={() => onMaxWidthChange(Math.max(MIN_WIDTH, maxWidth - STEP))}
          disabled={maxWidth <= MIN_WIDTH}
        >
          −
        </button>
        <input
          type="range"
          min={MIN_WIDTH}
          max={MAX_WIDTH}
          step={STEP}
          value={maxWidth}
          onChange={(e) => onMaxWidthChange(Number(e.target.value))}
          className={styles.sizeSlider}
        />
        <button
          className={styles.sizeBtn}
          onClick={() => onMaxWidthChange(Math.min(MAX_WIDTH, maxWidth + STEP))}
          disabled={maxWidth >= MAX_WIDTH}
        >
          +
        </button>
        <span className={styles.sizeLabel}>{maxWidth}px</span>
      </div>

      <div
        className={styles.imageContainer}
        style={{ maxWidth }}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        {!imageLoaded && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
          </div>
        )}

        <img
          ref={imgRef}
          src={previewUrl}
          alt={`B-scan ${bscanIndex}`}
          className={styles.image}
          onLoad={() => setImageLoaded(true)}
          style={{ display: imageLoaded ? 'block' : 'none' }}
        />

        {showMagnifier && imageLoaded && imgRef.current && (
          <div
            className={styles.magnifier}
            style={{
              width: MAGNIFIER_SIZE,
              height: MAGNIFIER_SIZE,
              left: magnifierPos.x - MAGNIFIER_SIZE / 2,
              top: magnifierPos.y - MAGNIFIER_SIZE / 2,
              backgroundImage: `url(${previewUrl})`,
              backgroundSize: `${imgRef.current.offsetWidth * ZOOM_LEVEL}px ${imgRef.current.offsetHeight * ZOOM_LEVEL}px`,
              backgroundPositionX: -(magnifierPos.x * ZOOM_LEVEL - MAGNIFIER_SIZE / 2),
              backgroundPositionY: -(magnifierPos.y * ZOOM_LEVEL - MAGNIFIER_SIZE / 2),
            }}
          />
        )}

        {isLoading && (
          <div className={styles.overlay}>
            <div className={styles.spinner} />
          </div>
        )}
      </div>

      <div className={styles.hint}>
        Hover over the image to magnify
      </div>
    </div>
  );
}

export default BScanViewer;
