/**
 * Shared severity-related utilities.
 */

export const SEVERITY_CLASSES = ['Normal', 'Mild', 'Moderate', 'Severe'];

export const severityColorMap = {
  Normal: 'bg-emerald-500 shadow-emerald-500/40',
  Mild: 'bg-amber-500 shadow-amber-500/40',
  Moderate: 'bg-coral shadow-coral/40',
  Severe: 'bg-red-500 shadow-red-500/40',
};

export const severityValue = {
  Normal: 1,
  Mild: 2,
  Moderate: 3,
  Severe: 4,
};

export function getHighlightStyle(weight) {
  if (weight === 3) return { backgroundColor: 'rgba(239, 68, 68, 0.3)', color: '#7f1d1d' };
  if (weight === 2) return { backgroundColor: 'rgba(226, 114, 91, 0.3)', color: '#7c2d12' };
  if (weight === 1) return { backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#78350f' };
  return { color: '#334155' };
}
