# python/acquire.py
import cv2, serial, time, csv, os, sys, yaml, math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def load_cfg(path="config.yaml"):
    if os.path.exists(path):
        with open(path) as f: return yaml.safe_load(f)
    return {
        "camera_index": 0,
        "serial_port": "COM5",   # or "/dev/ttyUSB0"
        "baud": 115200,
        "roi": [0.4, 0.4, 0.2, 0.2],  # x,y,w,h in relative coords (centered spot)
        "save_dir": "../results/runs",
        "duration_s": 300,
        "save_frames": True,
        "intensity_change_thresh": 12.0  # save frame if |ΔI| > thresh
    }

def roi_rect(frame, roi_rel):
    h, w = frame.shape[:2]
    x = int((roi_rel[0])*w); y = int((roi_rel[1])*h)
    ww = int((roi_rel[2])*w); hh = int((roi_rel[3])*h)
    x0 = max(0, x - ww//2); y0 = max(0, y - hh//2)
    x1 = min(w, x0 + ww);   y1 = min(h, y0 + hh)
    return x0, y0, x1, y1

def snr_est(region):
    m = region.mean()
    s = region.std() + 1e-9
    return float(m/s)

def main():
    cfg = load_cfg()
    cap = cv2.VideoCapture(cfg["camera_index"])
    if not cap.isOpened(): sys.exit("Camera not found")
    ser = serial.Serial(cfg["serial_port"], cfg["baud"], timeout=0.5)

    os.makedirs(cfg["save_dir"], exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(cfg["save_dir"], run_id)
    thumbs = os.path.join(run_dir, "frames"); os.makedirs(thumbs, exist_ok=True)
    csv_path = os.path.join(run_dir, "log.csv")
    meta_path = os.path.join(run_dir, "meta.txt")
    with open(meta_path,"w") as f: f.write(str(cfg))

    plt.ion()
    fig, ax = plt.subplots()
    ts, temps, intens = [], [], []
    last_I = None

    with open(csv_path, "w", newline="") as f:
        wr = csv.writer(f); wr.writerow(["timestamp","tempC","mean_intensity","snr","roi_x","roi_y","roi_w","roi_h"])
        t0 = time.time()
        while time.time() - t0 < cfg["duration_s"]:
            ret, frame = cap.read()
            if not ret: continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            x0,y0,x1,y1 = roi_rect(gray, cfg["roi"])
            roi = gray[y0:y1, x0:x1]
            I = float(roi.mean())
            SNR = snr_est(roi)

            line = ser.readline().decode(errors="ignore").strip()
            tempC = None
            if line.startswith("T,"):
                try: tempC = float(line.split(",")[1])
                except: pass

            now = time.time()-t0
            if tempC is not None:
                ts.append(now); temps.append(tempC); intens.append(I)
                wr.writerow([now, tempC, I, SNR, x0,y0,(x1-x0),(y1-y0)])

                # plot live
                ax.clear()
                ax.plot(ts, intens, label="Intensity (a.u.)")
                ax.plot(ts, temps,  label="Temp (°C)")
                ax.set_xlabel("Time (s)"); ax.legend(); plt.pause(0.001)

                # save frame on change
                if cfg["save_frames"] and last_I is not None and abs(I-last_I) > cfg["intensity_change_thresh"]:
                    fname = os.path.join(thumbs, f"t{int(now)}_I{int(I)}.png")
                    cv2.rectangle(frame, (x0,y0), (x1,y1), (0,255,0), 2)
                    cv2.imwrite(fname, frame)
                last_I = I

        plt.ioff(); plt.savefig(os.path.join(run_dir, "intensity_temp_timeseries.png"), dpi=180)
    cap.release(); ser.close()
    print("Saved:", run_dir)

if __name__ == "__main__":
    main()
