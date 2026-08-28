import pynvml

class GPUTelemetry:
    def __init__(self, device_index=0):
        pynvml.nvmlInit()
        self.handle = pynvml.nvmlDeviceGetHandleByIndex(device_index)
        
    def get_metrics(self):
        # Temperature in Celsius
        temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)
        # Power consumption in Watts (converted from mW)
        power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000.0
        return {"temp": temp, "power": power}

    def __del__(self):
        try:
            pynvml.nvmlShutdown()
        except:
            pass