# camera_only_logger.py
import cv2, time, csv, numpy as np
cap = cv2.VideoCapture(0)  # try 1 if 0 isn't your webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # manual exposure on some cams
cap.set(cv2.CAP_PROP_EXPOSURE, -6)         # tweak to avoid saturation

roi = None  # set later by first frame
t0 = time.time()
with open("intensity_log.csv","w",newline="") as f:
    wr = csv.writer(f); wr.writerow(["t_s","mean_intensity","snr","roi"])
    while True:
        ok, frame = cap.read()
        if not ok: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # pick ROI once (center 25% box)
        if roi is None:
            h,w = gray.shape
            x0,y0,x1,y1 = int(w*0.375), int(h*0.375), int(w*0.625), int(h*0.625)
            roi = (x0,y0,x1,y1)

        x0,y0,x1,y1 = roi
        patch = gray[y0:y1, x0:x1]
        meanI = float(patch.mean())
        snr   = float(patch.mean()/(patch.std()+1e-9))
        wr.writerow([time.time()-t0, meanI, snr, roi])

        # optional preview box
        cv2.rectangle(frame,(x0,y0),(x1,y1),(0,255,0),1)
        cv2.imshow("preview", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release(); cv2.destroyAllWindows()
