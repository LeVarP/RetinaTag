/**
 * Labeling page - main UI for keyboard-first B-scan labeling.
 * Placeholder for Phase 6 implementation.
 */

import { useParams } from 'react-router-dom';

function LabelingPage() {
  const { scanId } = useParams<{ scanId: string }>();

  return (
    <div className="container">
      <h2>Labeling: {scanId}</h2>
      <p>This page will provide keyboard-first labeling interface.</p>
      <p>Phase 6: To be implemented</p>
    </div>
  );
}

export default LabelingPage;
