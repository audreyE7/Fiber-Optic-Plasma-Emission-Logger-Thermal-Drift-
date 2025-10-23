# python/analyze_run.py
import pandas as pd, numpy as np, matplotlib.pyplot as plt, sys, os

run_dir = sys.argv[1] if len(sys.argv)>1 else "../results/runs/last_run_dir_here"
df = pd.read_csv(os.path.join(run_dir,"log.csv"))
# smooth
df["I_smooth"] = df["mean_intensity"].rolling(5, min_periods=1).mean()
# simple correlation
corr = np.corrcoef(df["tempC"], df["I_smooth"])[0,1]
print(f"Temp–Intensity correlation: {corr:.3f}")

fig,ax1 = plt.subplots()
ax1.plot(df["timestamp"], df["I_smooth"], label="Intensity", linewidth=2)
ax2 = ax1.twinx()
ax2.plot(df["timestamp"], df["tempC"], color="tab:orange", label="Temp (°C)", alpha=0.7)
ax1.set_xlabel("Time (s)"); ax1.set_ylabel("Intensity (a.u.)"); ax2.set_ylabel("Temp (°C)")
fig.legend(loc="upper right"); fig.suptitle(f"Run summary (corr={corr:.2f})")
plt.tight_layout(); plt.savefig(os.path.join(run_dir,"summary.png"), dpi=180)
