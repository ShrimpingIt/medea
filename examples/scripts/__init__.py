from medea.agnostic import freq, ticks_ms, ticks_diff
freq(160000000)

def timeit(fun):
    startMs = ticks_ms()
    fun()
    stopMs = ticks_ms()
    print("Took:", ticks_diff(stopMs, startMs))