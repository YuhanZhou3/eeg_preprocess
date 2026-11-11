# EEG Preprocessing

A modular Python toolkit for loading, reconstructing, and preprocessing EEG/ECoG recordings stored in MATLAB `.mat` files, with an emphasis on handling artifact-removed signals and extracting spectral features.

## Overview

This repository provides a preprocessing pipeline for EEG/ECoG data, covering:

- **Data loading:** Extracting animal-level recordings and time-window metadata from MATLAB `.mat` files.
- **Signal reconstruction:** Aligning cleaned signals with their corresponding raw recordings by restoring removed samples as `NaN` values.
- **Signal segmentation:** Identifying contiguous, valid signal segments while excluding missing or removed samples.
- **Spectral analysis:** Computing power spectral density (PSD) using Welch's method.
- **Feature extraction:** Calculating absolute and relative frequency-band power across standard EEG frequency bands.

The pipeline is designed to preserve the temporal structure of artifact-removed recordings, avoiding the introduction of artificial discontinuities when performing spectral analysis.

## Project Structure

```text
EEG-Preprocess/
│
├── config.py          # Global configurations and constants
├── utils.py           # Signal alignment and segmentation utilities
├── data_loader.py     # MATLAB data loading and data access
├── preprocess.py      # Signal preprocessing and spectral feature extraction
└── README.md
```

## Modules

### 1. `config.py`

Centralizes preprocessing configurations and constants.

| Parameter | Default | Description |
|---|---:|---|
| `FS` | 256 Hz | Sampling frequency |
| `WINDOW` | 2 s | Welch window duration |
| `OVERLAP` | 0.5 | Welch window overlap ratio |
| `TOTAL_RANGE` | 0.5–100 Hz | Total frequency range |

Frequency bands:

| Band | Frequency Range |
|---|---|
| Delta | 0.5–4 Hz |
| Theta | 4–8 Hz |
| Alpha | 8–13 Hz |
| Beta | 13–30 Hz |
| Gamma | 30–100 Hz |

### 2. `utils.py`

Provides signal-processing utilities:

- `check_subseq(x, y)`: Checks whether a cleaned signal is an order-preserving subsequence of its original raw signal.
- `pad(x, y)`: Reconstructs the original signal timeline by inserting `NaN` values at removed sample positions.
- `find_segments(data, min_len)`: Identifies contiguous, non-NaN segments that satisfy a minimum length requirement.

The reconstruction step preserves the original temporal positions of valid samples, allowing subsequent analyses to operate on continuous signal segments rather than concatenated, potentially discontinuous recordings.

### 3. `data_loader.py`

Implements the `EEGDataLoader` class for loading and organizing MATLAB EEG/ECoG datasets.

**Main functionality:**

- Loads recordings from multiple `.mat` files, organized by drug or experimental condition.
- Extracts animal-level recordings and individual time windows.
- Organizes metadata and signals into a Pandas DataFrame.
- Optionally reconstructs cleaned signals and identifies valid contiguous segments.
- Provides a query interface for retrieving raw or cleaned recordings.

**Example:**

```python
from data_loader import EEGDataLoader

fpaths = {
    "Psilocybin": "data/PsilocybinEEG.mat",
    "LSD": "data/LSDEEG.mat",
}

loader = EEGDataLoader(fpaths, preprocess_clean=True)

# Retrieve a cleaned, NaN-padded recording
signal = loader.query(
    drug="psi",
    animal=1,
    window=0,
    clean=True,
    padded=True
)
```

The DataFrame uses a multi-index consisting of:

- `drug_abbr`
- `animal_idx`
- `window_idx`

Each recording retains its associated metadata, raw signal, cleaned signal, reconstructed signal, and valid segments.

### 4. `preprocess.py`

Provides spectral feature extraction based on Welch's power spectral density estimation.

**`band_powers_segments(segments, fs, bands, nperseg)`**

Computes PSD independently for each sufficiently long, contiguous signal segment.

The resulting PSD estimates are combined using segment-length-weighted averaging.

For each frequency band, the function calculates:

- **Absolute power:** Integrated PSD within the frequency band.
- **Relative power:** Absolute band power normalized by total power.

The function returns:

```python
features, frequencies, psd
```

Where:
- `features`: Dictionary containing absolute and relative band-power features.
- `frequencies`: Frequency bins from Welch's PSD estimation.
- `psd`: Length-weighted average PSD across valid segments.

**Example:**

```python
from preprocess import band_powers_segments

segments = loader.df.iloc[0]["clean_segments"]

features, frequencies, psd = band_powers_segments(segments)

print(features)
```

Example feature dictionary:

```python
{
    "total_power": ...,
    "abs_delta": ...,
    "rel_delta": ...,
    "abs_theta": ...,
    "rel_theta": ...,
    "abs_alpha": ...,
    "rel_alpha": ...,
    "abs_beta": ...,
    "rel_beta": ...,
    "abs_gamma": ...,
    "rel_gamma": ...
}
```

## Dependencies

- Python 3
- NumPy
- Pandas
- SciPy
- Numba

Install dependencies:

```bash
pip install numpy pandas scipy numba
```

## Design Considerations

### Preserving Temporal Continuity

Artifact removal can result in cleaned recordings containing samples that are no longer temporally adjacent in the original signal.

Simply concatenating the remaining samples can introduce artificial discontinuities, potentially distorting spectral estimates.

This pipeline addresses the issue by:

1. Matching cleaned samples to their original positions.
2. Reconstructing the original timeline using `NaN` padding.
3. Splitting the reconstructed signal into contiguous valid segments.
4. Computing PSD independently on each segment.
5. Combining segment-level PSD estimates through length-weighted averaging.

This approach avoids calculating Welch PSD across artificial splice boundaries.

## Future Development

Potential extensions include:

- Additional time-domain and frequency-domain features.
- Spectral entropy and signal complexity measures.
- Automated artifact detection and rejection.
- EMG feature extraction (if any).
- Time-resolved spectral analysis.
- Batch feature extraction and dataset export.
- Integration with downstream machine-learning pipelines.

<!-- ## License

License to be determined. -->