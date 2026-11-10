# Configurations / Constants 

FS = 256 # sampling frequency (f_s); unit = sample/sec

BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
    "gamma": (30, 100), 
}

TOTAL_RANGE = (0.5, 100)

# pwelch constraints
WINDOW = 2      # 2 second window
OVERLAP = 0.5   # 50% overlap