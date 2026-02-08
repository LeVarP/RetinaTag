/**
 * B-scan viewer component for displaying preview images.
 */

import { useState } from 'react';
import { Label, LabelNames } from '@/types';
import styles from './BScanViewer.module.css';

interface BScanViewerProps {
  previewUrl: string;
  label: Label;
  bscanIndex: number;
  isLoading?: boolean;
}

function BScanViewer({
  previewUrl,
  label,
  bscanIndex,
  isLoading = false,
}: BScanViewerProps) {
  const [imageLoaded, setImageLoaded] = useState(false);

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

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <span className={styles.index}>B-scan #{bscanIndex}</span>
        <span className={`${styles.labelBadge} ${getLabelClass()}`}>
          {LabelNames[label]}
        </span>
      </div>

      <div className={styles.imageContainer}>
        {!imageLoaded && (
          <div className={styles.loading}>
            <div className={styles.spinner} />
          </div>
        )}

        <img
          src={previewUrl}
          alt={`B-scan ${bscanIndex}`}
          className={styles.image}
          onLoad={() => setImageLoaded(true)}
          style={{ display: imageLoaded ? 'block' : 'none' }}
        />

        {isLoading && (
          <div className={styles.overlay}>
            <div className={styles.spinner} />
          </div>
        )}
      </div>
    </div>
  );
}

export default BScanViewer;
