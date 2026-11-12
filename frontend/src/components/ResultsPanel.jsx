import { useMemo } from 'react';

export default function ResultsPanel({ result }) {
  if (!result) return null;

  const { predicted_class, confidence, highlighted_tokens, class_probabilities } = result;

  const getHighlightColor = (weight) => {
    if (weight === 0) return 'transparent';
    if (weight === 1) return 'rgba(245, 158, 11, 0.2)'; // Mild - Amber tint
    if (weight === 2) return 'rgba(226, 114, 91, 0.4)'; // Moderate - Coral tint
    if (weight === 3) return 'rgba(239, 68, 68, 0.4)';  // Severe - Red tint
    return 'transparent';
  };

  const getWeightLabel = (weight) => {
    if (weight === 1) return 'Mild indicator';
    if (weight === 2) return 'Moderate indicator';
    if (weight === 3) return 'Severe indicator';
    return '';
  };

  const explanationSentence = useMemo(() => {
    const importantPhrases = highlighted_tokens
      .filter(t => t.weight >= 2)
      .map(t => t.text.trim())
      .filter(Boolean);
    
    if (importantPhrases.length > 0) {
      // Get unique phrases up to 3
      const unique = [...new Set(importantPhrases)].slice(0, 3);
      return `This post was classified as ${predicted_class} primarily due to the phrases: '${unique.join("', '")}'.`;
    } else if (predicted_class !== "Normal") {
      const mildPhrases = highlighted_tokens.filter(t => t.weight === 1).map(t => t.text.trim());
      if (mildPhrases.length > 0) {
        const unique = [...new Set(mildPhrases)].slice(0, 3);
        return `This post was classified as ${predicted_class} due to phrases like: '${unique.join("', '")}'.`;
      }
    }
    return `This post was classified as ${predicted_class} as no significant distress indicators were detected.`;
  }, [highlighted_tokens, predicted_class]);

  return (
    <div className="card results-panel">
      <div className="results-header">
        <div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem', textTransform: 'uppercase', fontWeight: 600 }}>Predicted Severity</div>
          <div className={`severity-badge ${predicted_class}`}>
            {predicted_class}
          </div>
        </div>
        <div className="confidence-meter-container">
          <div className="confidence-label">Confidence</div>
          <div className="confidence-value">{confidence}%</div>
        </div>
      </div>

      <div className="chart-container">
        <h3 className="chart-title">Class Probabilities</h3>
        {['Normal', 'Mild', 'Moderate', 'Severe'].map(cls => (
          <div className="bar-row" key={cls}>
            <div className="bar-label">{cls}</div>
            <div className="bar-track">
              <div 
                className={`bar-fill ${cls}`} 
                style={{ width: `${class_probabilities[cls] || 0}%` }}
              ></div>
            </div>
            <div className="bar-value">{class_probabilities[cls] || 0}%</div>
          </div>
        ))}
      </div>

      <div className="explanation-container">
        <h3 className="explanation-title">Explainability Analysis</h3>
        <div className="highlighted-text">
          {highlighted_tokens.map((token, idx) => (
            <span 
              key={idx} 
              style={{ 
                backgroundColor: getHighlightColor(token.weight),
                borderRadius: '3px',
                padding: token.weight > 0 ? '0 2px' : '0'
              }}
              title={getWeightLabel(token.weight)}
            >
              {token.text}
            </span>
          ))}
        </div>
        <p className="explanation-sentence">{explanationSentence}</p>
      </div>
    </div>
  );
}
