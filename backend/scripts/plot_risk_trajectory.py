import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

# Mock 7-Day Data
days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7 (Today)']
# Severity: 0=Normal, 1=Mild, 2=Moderate, 3=Severe/Crisis
severity = [0.2, 0.5, 1.2, 1.0, 2.3, 2.8, 3.0] 
# CSI: 0 to 100% (Ratio of Tamil vocabulary used)
csi = [15, 20, 45, 30, 70, 85, 92] 

# Set up the plot aesthetics
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot 1: Risk Severity (Area Chart)
color = '#ef4444' # Red
ax1.set_xlabel('Time (7 Days)', fontweight='bold')
ax1.set_ylabel('Clinical Severity Score', color=color, fontweight='bold', fontsize=12)
ax1.plot(days, severity, color=color, linewidth=3, marker='o', label='Severity Score')
ax1.fill_between(days, severity, alpha=0.2, color=color)
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim(0, 3.5)
ax1.set_yticks([0, 1, 2, 3])
ax1.set_yticklabels(['0 (Normal)', '1 (Mild)', '2 (Moderate)', '3 (Severe)'], fontweight='bold')

# Plot 2: CSI (Line Chart on secondary Y-axis)
ax2 = ax1.twinx()  
color2 = '#3b82f6' # Blue
ax2.set_ylabel('Code-Switching Index (CSI %)', color=color2, fontweight='bold', fontsize=12)  
ax2.plot(days, csi, color=color2, linewidth=3, linestyle='--', marker='s', label='CSI (Tamil %)')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_ylim(0, 100)

# Add title and custom aesthetics
plt.title('Patient #402: 7-Day Risk Trajectory & Code-Switching Index', fontsize=16, fontweight='bold', pad=20)
fig.tight_layout()  

# Add a combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

# Highlight the correlation
ax1.annotate('Crisis Spike correlates with\nhigh native language usage (CSI)', 
            xy=(5.5, 2.9), xytext=(2, 3.2),
            arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
            fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1))

# Save the figure
out_path = os.path.join(os.path.dirname(__file__), 'risk_trajectory_chart.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Chart saved successfully to: {out_path}")
