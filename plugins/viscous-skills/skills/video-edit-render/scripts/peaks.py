import subprocess, sys, numpy as np
for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-map", "0:a", "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).reshape(-1, 2)
    pk = np.abs(x).max(axis=1)
    sec = [(i, 20*np.log10(pk[i*48000:(i+1)*48000].max()+1e-9)) for i in range(len(pk)//48000)]
    hot = [(i, round(d, 1)) for i, d in sec if d > -1.0]
    print(f, "max", round(20*np.log10(pk.max()), 2), "dBFS; seconds over -1 dBFS:", hot[:30])
