"""Hold ES_SYSTEM_REQUIRED for the night (Add-Type is broken on this box)."""
import ctypes, time
FLAGS = 2147483649  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
k = ctypes.windll.kernel32
prev = k.SetThreadExecutionState(FLAGS)
print("keep_awake_armed", prev, flush=True)
try:
    time.sleep(57600)
finally:
    k.SetThreadExecutionState(2147483648)  # ES_CONTINUOUS only = clear
print("keep_awake_released", flush=True)
