import argparse
from typing import List, Tuple, Optional
import os
import json
import yaml

def filter_pareto_optimal_points(a: List[float], b: List[float]) -> Tuple[List[float], List[float]]:
    """
    Filters points to keep only Pareto optimal ones.
    A point is Pareto optimal if there is no other point that dominates it
    (i.e., no other point has better or equal values in both dimensions).
    For minimization problems, lower values are better.
    """
    if len(a) != len(b):
        raise ValueError("Lists a and b must have the same length")
    
    if not a:
        return [], []
    
    # Create list of (index, a_val, b_val) tuples
    points = list(enumerate(zip(a, b)))
    
    # Sort by a values (ascending), then by b values (ascending) for ties
    points.sort(key=lambda x: (x[1][0], x[1][1]))
    
    pareto_indices = []
    min_b = float('inf')
    
    for idx, (a_val, b_val) in points:
        # If this point has a better (lower) b value than any previous point
        if b_val < min_b:
            pareto_indices.append(idx)
            min_b = b_val
    
    # Extract Pareto optimal points
    pareto_a = [a[i] for i in pareto_indices]
    pareto_b = [b[i] for i in pareto_indices]
    
    return pareto_a, pareto_b

def plot_pareto(title: str, json_path: str, design_config_path: str, output_dir: str, power: bool = False, remove_points: bool = False):
    """
    Plots Pareto curves for each design specified in design_config.
    Y-axis is delay, X-axis is power or area based on the power flag.
    """
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Load design configuration
    with open(design_config_path, 'r') as f:
        config = yaml.safe_load(f)
    designs = config.get('designs', [])
    
    # Load Pareto data
    with open(json_path, 'r') as f:
        pareto_data = json.load(f)
    
    # Set up the plot
    plt.figure(figsize=(10, 8))
    
    # Define colors for different designs
    colors = plt.cm.Set1(np.linspace(0, 1, len(designs)))
    
    for i, design in enumerate(designs):
        if design not in pareto_data:
            print(f"Warning: Design {design} not found in Pareto data, skipping.")
            continue
        
        # Extract data for this design
        delays = []
        x_values = []
        
        for clock_period, data in pareto_data[design].items():
            timing = data['timing']
            if timing == "VIOLATED" or timing is None:
                continue
            
            delays.append(timing)
            
            if power:
                x_val = data['power']
            else:
                x_val = data['area']
            
            if x_val is not None:
                x_values.append(x_val)
            else:
                delays.pop()  # Remove the corresponding delay if x_val is None
        
        if not delays or not x_values:
            print(f"Warning: No valid data points for design {design}, skipping.")
            continue
        
        # Filter Pareto optimal points if requested
        # if remove_points:
        pareto_x, pareto_delays = filter_pareto_optimal_points(x_values, delays)
        # Plot non-Pareto optimal points as scatter
        non_pareto_x = [x for x in x_values if x not in pareto_x]
        non_pareto_delays = [d for d, x in zip(delays, x_values) if x not in pareto_x]
        
        if non_pareto_x and not remove_points:
            plt.scatter(non_pareto_x, non_pareto_delays, 
                        color=colors[i], alpha=0.3, s=30, 
                        label=f'{design} (non-optimal)')
        
        # Plot Pareto optimal points and line
        if pareto_x:
            plt.plot(pareto_x, pareto_delays, 'o-', 
                    color=colors[i], linewidth=2, markersize=6,
                    label=f'{design} (Pareto optimal)')
    
    x_label = 'Power (W)' if power else 'Area (μm²)'
    plt.xlabel(x_label)
    plt.ylabel('Delay (ns)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{title}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Pareto plot saved to {output_path}")

def create_pareto_json(input_dir: str, design_config_path: str, output_dir: str):
    """
    Creates a pareto_data.json file in output_dir, containing synthesis results for each design and clock period.
    Clock periods are sorted by their timing values rather than directory names.
    """
    # Load design names from YAML config
    with open(design_config_path, 'r') as f:
        config = yaml.safe_load(f)
    designs = config.get('designs', [])

    pareto_data = {}
    for design in designs:
        design_dir = os.path.join(input_dir, design)
        reports_dir = os.path.join(design_dir, 'reports')
        if not os.path.isdir(reports_dir):
            print(f"Reports directory not found for design {design} at {reports_dir}, skipping.")
            continue
        
        # Collect all clock period data first
        clock_period_data = {}
        for clock_period in os.listdir(reports_dir):
            clock_dir = os.path.join(reports_dir, clock_period)
            if not os.path.isdir(clock_dir):
                print(f"Clock period directory {clock_period} not found for design {design}, skipping.")
                continue
            timing_path = os.path.join(clock_dir, 'timing.rpt')
            area_path = os.path.join(clock_dir, 'area.rpt')
            power_path = os.path.join(clock_dir, 'power.rpt')
            timing = parse_timing_report(timing_path) if os.path.isfile(timing_path) else None
            area = parse_area_report(area_path) if os.path.isfile(area_path) else None
            power = parse_power_report(power_path, 'Net Switching Power') if os.path.isfile(power_path) else None
            clock_period_data[clock_period] = {
                'timing': round(timing, 4) if timing is not None else "VIOLATED",
                'area': area,
                'power': power
            }
        
        # Sort clock periods by timing values
        # Handle cases where timing might be "VIOLATED" or None
        def get_timing_value_for_sorting(clock_period):
            timing_data = clock_period_data[clock_period]['timing']
            if timing_data == "VIOLATED" or timing_data is None:
                return float('inf')  # Put violated timing at the end
            return timing_data
        
        sorted_clock_periods = sorted(clock_period_data.keys(), 
                                    key=get_timing_value_for_sorting)
        
        # Create ordered dictionary with sorted clock periods
        pareto_data[design] = {}
        for clock_period in sorted_clock_periods:
            pareto_data[design][clock_period] = clock_period_data[clock_period]
    
    # Write to JSON file
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'pareto_data.json')
    with open(output_path, 'w') as f:
        json.dump(pareto_data, f, indent=2)

def parse_timing_report(report_path: str) -> Optional[float]:
    """
    Sums the 'Incr' column values from the line after the first '*/Q' line
    up to (but not including) the line before 'data arrival time' and returns the sum as a float.
    If 'VIOLATED' is found anywhere in the report, returns None.
    """
    # First pass: check for VIOLATED
    with open(report_path, 'r') as f:
        content = f.read()
        if 'VIOLATED' in content:
            return None
    
    # Second pass: parse timing data
    total = 0.0
    found_q = False
    with open(report_path, 'r') as f:
        for line in f:
            if not found_q:
                if '/Q' in line:
                    found_q = True
                continue
            if 'data arrival time' in line:
                break
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    incr_val = float(parts[2])
                    total += incr_val
                except ValueError:
                    print(f"Could not convert '{parts[2]}' to float, skipping line.")
                    pass  # skip lines that don't have a valid float
    return total

def parse_area_report(report_path: str) -> Optional[float]:
    """
    Extracts the value after 'Combinational area:' from the area report.
    Returns the value as a float, or None if not found.
    """
    with open(report_path, 'r') as f:
        for line in f:
            if 'Combinational area:' in line:
                parts = line.strip().split()
                # The value should be the last part of the line
                try:
                    return float(parts[-1])
                except ValueError:
                    return None
    return None

def parse_power_report(report_path: str, power_metric: str = 'Total Power') -> Optional[float]:
    """
    Extracts the value after 'Total Power =' from the power report.
    Returns the value as a float, or None if not found.
    """
    with open(report_path, 'r') as f:
        for line in f:
            if power_metric in line and '=' in line:
                parts = line.strip().split('=')
                if len(parts) >= 2:
                    value_str = parts[1].strip().split()[0]
                    try:
                        return float(value_str)
                    except ValueError:
                        return None
    return None

def main():
    parser = argparse.ArgumentParser(description="Plot synthesis results and Pareto curves.")
    parser.add_argument('--input_dir', '-i', required=True, help='Path to directory containing synthesis results for different designs')
    parser.add_argument('--design_config', '-d', required=True, help='Path to YAML config file with different designs to be plotted')
    parser.add_argument('--output_dir', '-o', required=True, help='Path to output directory where plots will be saved')
    parser.add_argument('--remove_points', '-r', action='store_true', help='Remove non-pareto optimal points from graph')
    parser.add_argument('--module_name', '-m', required=True, help='Name of the top module of the design')
    parser.add_argument('--power', '-p', action='store_true', help='Use power as X-axis instead of area')
    parser.add_argument('--title', '-t', required=True, help='Title of the plot')
    args = parser.parse_args()

    # Create Pareto JSON data
    create_pareto_json(args.input_dir, args.design_config, args.output_dir)
    
    # Generate Pareto plots
    json_path = os.path.join(args.output_dir, 'pareto_data.json')
    
    print(f"Plotting {args.module_name} with area as X-axis")
    # Plot with area as X-axis
    plot_pareto(
        title=f"{args.module_name}_Area_vs_Delay",
        json_path=json_path,
        design_config_path=args.design_config,
        output_dir=args.output_dir,
        power=False,
        remove_points=args.remove_points
    )
    
    print(f"Plotting {args.module_name} with power as X-axis")
    # Plot with power as X-axis
    plot_pareto(
        title=f"{args.module_name}_Power_vs_Delay",
        json_path=json_path,
        design_config_path=args.design_config,
        output_dir=args.output_dir,
        power=True,
        remove_points=args.remove_points
    )

if __name__ == "__main__":
    main()
