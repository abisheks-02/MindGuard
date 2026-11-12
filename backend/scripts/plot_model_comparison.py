import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# Data
models = ['B1: Lexicon', 'B2: Translate+VADER', 'B3: TF-IDF+LR', 'MindGuard (Proposed)']
sensitivity = [40.2, 55.4, 71.0, 94.5]
specificity = [98.1, 72.3, 88.5, 92.0]

x = np.arange(len(models))
width = 0.35

# Set up the plot aesthetics
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(10, 6))

# Create grouped bars
rects1 = ax.bar(x - width/2, sensitivity, width, label='Sensitivity (Crisis Recall)', color='#ef4444', edgecolor='black', linewidth=1)
rects2 = ax.bar(x + width/2, specificity, width, label='Specificity (False Alarm Avoidance)', color='#3b82f6', edgecolor='black', linewidth=1)

# Add text for labels, title and custom x-axis tick labels
ax.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
ax.set_title('Clinical Triage Metrics: MindGuard vs Baselines', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(models, fontsize=11, fontweight='bold')
ax.legend(loc='lower right', fontsize=11)
ax.set_ylim(0, 110)

# Add value labels on top of bars
def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', fontsize=10)

autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

# Save the figure
out_path = os.path.join(os.path.dirname(__file__), 'model_comparison_chart.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved successfully to: {out_path}")
