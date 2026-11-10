import numpy as np
from scipy.signal import welch
from scipy.integrate import trapezoid
from config import FS, BANDS

def band_powers_segments(segments, fs=FS, bands=BANDS, nperseg=2*FS):
    """ Compute Welch on each contiguous segment and average, weighting by length
    segments: list of 1D arrays (contiguous clean pieces).
    """
    psds, weights = [], []
    for seg in segments:
        if seg.size < nperseg:          # too short for even one window
            continue
        f, p = welch(seg, fs=fs, nperseg=nperseg)
        psds.append(p)
        weights.append(seg.size)
    if not psds:
        return {name: np.nan for name in bands}, f, np.nan
    psd = np.average(psds, axis=0, weights=weights)
    out = {}
    
    total_lo, total_hi = min(lo for lo, _ in bands.values()), max(hi for _, hi in bands.values())
    total_idx = (f >= total_lo) & (f < total_hi)
    total_power = trapezoid(psd[total_idx], f[total_idx])
    out["total_power"] = total_power
    for name, (lo, hi) in bands.items():
        idx = (f >= lo) & (f < hi)
        out[f"abs_{name}"] = trapezoid(psd[idx], f[idx])
        out[f"rel_{name}"] = out[f"abs_{name}"] / total_power
    return out, f, psd