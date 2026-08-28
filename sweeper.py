from telemetry import GPUTelemetry
import kernels
import time

class SiliconSweeper:
    def __init__(self):
        self.gpu_mon = GPUTelemetry(0)

    def run_full_profile(self, iterations: int):
        base = self.gpu_mon.get_metrics()

        # FP32 ALU Benchmark
        start_time = time.time()
        t_end = start_time + 2.0
        alu_runs = 0
        alu_sum = 0
        while time.time() < t_end:
            alu_sum = kernels.run_alu_stress(iterations)
            alu_runs += 1
        alu_duration = time.time() - start_time
        peak_alu = self.gpu_mon.get_metrics()

        total_alu_ops = (1024 * 1024) * iterations * alu_runs * 2
        alu_tflops = (total_alu_ops / alu_duration) / 1e12 if alu_duration > 0 else 0.0

        # Tensor Cores Benchmark
        start_time = time.time()
        t_end = start_time + 2.0
        tensor_runs = 0
        tensor_sum = 0
        while time.time() < t_end:
            tensor_sum = kernels.run_tensor_stress(iterations)
            tensor_runs += 1
        tensor_duration = time.time() - start_time
        peak_tensor = self.gpu_mon.get_metrics()

        total_tensor_ops = 128 * 32 * (16 * 16 * 16 * 2) * tensor_runs
        tensor_tflops = (total_tensor_ops / tensor_duration) / 1e12 if tensor_duration > 0 else 0.0

        total_duration = alu_duration + tensor_duration

        return {
            "duration": total_duration,
            "iterations": iterations,
            "baseline": base,
            "alu": {
                "sum": alu_sum,
                "tflops": alu_tflops,
                "peak_temp": peak_alu['temp'],
                "temp_delta": peak_alu['temp'] - base['temp'],
                "power_delta": peak_alu['power'] - base['power']
            },
            "tensor": {
                "sum": tensor_sum,
                "tflops": tensor_tflops,
                "peak_temp": peak_tensor['temp'],
                "temp_delta": peak_tensor['temp'] - base['temp'],
                "power_delta": peak_tensor['power'] - base['power']
            }
        }

    def find_stability_limit(self, max_iterations=500000, step=25000):
        """Automatic Search for the Stability Limit of Silicon Using Incremental Iteration."""
        current_iters = step
        last_stable_results = None

        while current_iters <= max_iterations:
            print(f"[*] Iteration Threshold Testing: {current_iters:,}...")
            try:
                res = self.run_full_profile(iterations=current_iters)
                if res["alu"]["sum"] == 0 or res["tensor"]["sum"] == 0:
                    print(f"[!] A calculation error was detected at the threshold {current_iters:,}")
                    break
                last_stable_results = res
                current_iters += step
            except Exception as e:
                print(f"[!] Driver/kernel failure at iterations {current_iters:,}: {e}")
                break

        return last_stable_results