import numpy as np
import numba
from config import *

def check_subseq(x, y) -> bool:
    """Check if y is an order-preserving subsequence of x"""
    j = 0
    for v in x:
        if j < len(y) and v == y[j]:
            j += 1
    return j == len(y)

@numba.njit
def _pad_nan(x, y):
    """Pad y with NaN to match the length of x, given that y is an order-preserving subsequence of x. """
    out = np.full(len(x), np.nan)
    j = 0
    for i in range(len(x)):
        if j < len(y) and x[i] == y[j]:
            out[i] = x[i]
            j += 1
            
    if j != len(y):
        raise ValueError("Couldn't match all values.")
    return out

def pad(x, y):
    """ Check if y is an order-preserving subsequence of x, and if so pad y with NaN to match the length of x. """
    if not check_subseq(x, y):
        raise ValueError("Failed order-preserving subsequence check. Cannot pad sequence.")
    return _pad_nan(x, y)

def find_segments(data, min_len=2*FS):
    """ Find segments of contiguous non-NaN values in [data] that are at least [min_len] long."""
    valid = ~np.isnan(data)
    d = np.diff(valid.astype(int), prepend=0, append=0) # x[i+1] - x[i]
    starts = np.where(d==1)[0]
    ends = np.where(d==-1)[0]
    return [(s, e) for s, e in zip(starts, ends) if e - s >= min_len]