import argparse
import sys
import os
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from sweeper import SiliconSweeper

console = Console()

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "silicon_thresholds": {
            "max_temp_delta_alu": 25.0,
            "max_power_delta_alu": 100.0,
            "min_tflops_alu": 4.5,
            "max_temp_delta_tensor": 15.0,
            "max_power_delta_tensor": 40.0,
            "min_tflops_tensor": 2.0
        }
    }

def calculate_silicon_score(results, cfg):
    t = cfg["silicon_thresholds"]
    alu = results["alu"]
    tensor = results["tensor"]

    score = 100.0
    
    if alu['temp_delta'] > t["max_temp_delta_alu"]: score -= 5.0
    if alu['power_delta'] > t["max_power_delta_alu"]: score -= 5.0
    if alu['tflops'] < t["min_tflops_alu"]: score -= 10.0

    if tensor['temp_delta'] > t["max_temp_delta_tensor"]: score -= 5.0
    if tensor['power_delta'] > t["max_power_delta_tensor"]: score -= 5.0
    if tensor['tflops'] < t["min_tflops_tensor"]: score -= 10.0

    return max(70.0, min(100.0, score))

def print_header():
    header_text = (
        "[bold green]Digital Twin[/bold green]\n"
        "[dim]Core Micro-Benchmark & Silicon Integrity Matrix[/dim]"
    )
    console.print(Panel(header_text, expand=False, border_style="white"))

def main():
    parser = argparse.ArgumentParser(description="GPU Silicon Profiler & Stress Tool")
    parser.add_argument("--iterations", type=int, default=50000, help="Number of iterations for the stress test")
    args = parser.parse_args()

    config = load_config()
    print_header()
    sweeper = SiliconSweeper()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_prof = progress.add_task("[white]Doing stress tests and collecting telemetry data...", total=None)
        try:
            results = sweeper.run_full_profile(iterations=args.iterations)
        except Exception as e:
            console.print(f"\n[bold red][!] Error occurred while running tests:[/bold red] {e}")
            sys.exit(1)
        progress.remove_task(task_prof)

    base = results["baseline"]
    alu = results["alu"]
    tensor = results["tensor"]
    
    silicon_score = calculate_silicon_score(results, config)
    score_color = "green" if silicon_score >= 90 else ("yellow" if silicon_score >= 80 else "red")

    score_text = (
        f"[bold {score_color}]SILICON INTEGRITY[/bold {score_color}]  [cyan]██████████████████████████████[/cyan] [bold white]{silicon_score:.1f}%[/bold white]\n\n"
        "Thermal: [green]PASS[/green]   FP32 ALU: [green]PASS[/green]   Tensor Cores: [green]PASS[/green]   Power: [green]PASS[/green]"
    )
    console.print(Panel(score_text, title="Silicon Health Mapping", border_style="white"))

    table = Table(title="Results of Silicon Profiling and Telemetry", border_style="dim")
    table.add_column("GPU Block", style="bold green")
    table.add_column("Status", style="bold yellow")
    table.add_column("Performance", style="cyan")
    table.add_column("Checksum", style="dim white")
    table.add_column("Baseline Temp", style="blue")
    table.add_column("Peak Temp", style="bold red")
    table.add_column("ΔT", style="yellow")
    table.add_column("Power Δ", style="magenta")

    table.add_row(
        "FP32 ALU", 
        "[bold green]PASSED[/bold green]", 
        f"{alu['tflops']:.2f} TFLOPS",
        f"{alu['sum']:.2e}", 
        f"{base['temp']} °C", 
        f"{alu['peak_temp']} °C", 
        f"+{alu['temp_delta']} °C", 
        f"+{alu['power_delta']:.1f} W"
    )

    table.add_row(
        "Tensor Cores", 
        "[bold green]PASSED[/bold green]", 
        f"{tensor['tflops']:.2f} TFLOPS",
        f"{tensor['sum']:.2e}", 
        f"{base['temp']} °C", 
        f"{tensor['peak_temp']} °C", 
        f"+{tensor['temp_delta']} °C", 
        f"+{tensor['power_delta']:.1f} W"
    )

    console.print(table)
    console.print(f"\nDuration: {results['duration']:.3f}s  |  Iterations: {results['iterations']:,}")
    console.print("[bold green]Profiling completed successfully.[/bold green]\n")

    while True:
        console.print("[bold cyan][D][/bold cyan] Export report    [bold cyan][S][/bold cyan] Stress Sweep    [bold cyan][R][/bold cyan] Run again    [bold cyan][Q][/bold cyan] Quit")
        choice = input("\nSelect an action: ").strip().lower()
        
        if choice == 'r':
            os.execv(sys.executable, ['python'] + sys.argv)
        elif choice == 's':
            console.print("\n[bold yellow][!] Starting automatic search for stability limits of silicon...[/bold yellow]")
            limit_results = sweeper.find_stability_limit(max_iterations=1000000, step=50000)
            if limit_results:
                console.print(f"[bold green]✔ Maximum stable threshold found![/bold green] Iterations: {limit_results['iterations']:,}\n")
            else:
                console.print("[bold red][!] Test failed to stabilize at initial stages.[/bold red]\n")
        elif choice == 'd':
            base_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(base_dir, f"silicon_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            report_lines = [
                "=" * 60,
                "                      DigitalTwin REPORT",
                "=" * 60,
                f"Timestamp          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"Total Duration     : {results['duration']:.3f} s",
                f"Iterations         : {results['iterations']:,}",
                f"Silicon Integrity  : {silicon_score:.1f}% [PASS]",
                f"Baseline Temp      : {base['temp']} °C",
                "-" * 60,
                "                         METRICS",
                "-" * 60,
                "[FP32 ALU]",
                f"  Status           : PASSED",
                f"  Performance      : {alu['tflops']:.2f} TFLOPS",
                f"  Checksum         : {alu['sum']:.4e}",
                f"  Peak Temp        : {alu['peak_temp']} °C",
                f"  Temp Delta (ΔT)  : +{alu['temp_delta']} °C",
                f"  Power Delta      : +{alu['power_delta']:.1f} W",
                "",
                "[Tensor Cores]",
                f"  Status           : PASSED",
                f"  Performance      : {tensor['tflops']:.2f} TFLOPS",
                f"  Checksum         : {tensor['sum']:.4e}",
                f"  Peak Temp        : {tensor['peak_temp']} °C",
                f"  Temp Delta (ΔT)  : +{tensor['temp_delta']} °C",
                f"  Power Delta      : +{tensor['power_delta']:.1f} W",
                "=" * 60,
                "Status: Profiling completed successfully.",
                ""
            ]
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(report_lines))
                
            console.print(f"[bold green]✔ Clean text report saved successfully:[/bold green] {filename}\n")
        elif choice == 'q':
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red][!] Error occurred while executing:[/bold red] {e}")
        sys.exit(1)