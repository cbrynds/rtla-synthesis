# RTLA Synthesis Environment

A synthesis environment configured for Synopsys RTL Architect (RTLA) using a 32nm Synopsys PDK with design corner analysis. Tailored for the purpose of pareto curve generation.

## Prerequisites

### Software Requirements
- Synopsys RTL Architect (RTLA)
- 32nm Synopsys PDK
- Python 3.7+
- Synopsys PrimePower (For power analysis)

### System Requirements
- Linux environment (tested on RHEL/CentOS 8)
- Minimum 8GB RAM
- X11 forwarding capability (for GUI tools)

## Directory Structure

```
rtla-synthesis/
├── base-synthesis-dir/                 # Top level of synthesis environment
│   ├── data/
│   │   ├── constraints/                # Contains design constraints, corners, and scenario data
│   │   ├── ndm/                        # Contains technology files for 32nm PDK
│   │   └── rtl/                        # Stores user's RTL design to be synthesized
│   └── scripts/
│       ├── clean_dir.sh                # Script to remove RTLA files and metadeta. Warning: will clear reports directory
│       ├── run_synthesis.tcl           # Analyzes and elaborates RTL files and then performs FAST physical-aware synthesis
│       └── setup.tcl                   # Creates design library and loads technology files
├── pareto_synthesis.tcl                # Top-level synthesis script to generate pareto curves
├── plot_synthesis_results.py           # Script to plot pareto curves
└── README.md                           # This file
```

## Usage

For each design to be evaluated, create a renamed copy of `base-synthesis-dir/` under the same top-level directory

Copy the RTL files of the design into `data/rtl` inside of the newly-copied directory. It is important that the top module name matches the name of the file in which it is located

Navigate inside the copied directory and run

`rtl_shell -f pareto_synthesis.tcl -x "set DESIGN_NAME <top module name>"`

This will launch the RTL Architect tool and begin pareto curve generation. The script will exit RTLA automatically once complete.

**Note**: By default, this script is configured to read in SystemVerilog files. Change line 18 of `scripts/run_synthesis.tcl` if you are synthesizing Verilog or VHDL files

## Configuration

### Synthesis Configuration

The synthesis environment is configured for the following four design corners:

1. **FF1p16125c**: Short path delay, highest leakage current
2. **FF1p1640c**: Shortest path delays, worst-case for hold timing, higher switching power, lower leakage
3. **SS0p95v125c**: Longest path delays, worst-case for setup timing, higher leakage
4. **SS0p95v40c**: Long path delays, low leakage

## Pareto Curve Generation

The script `pareto_synthesis.tcl` contains the logic for generating a pareto curve for a given design. It uses the following procedure for curve generation:

1. Select an extremely small clock period target that is expected to be violated (default is 0.01 ns)
2. Synthesize the design and check the timing report
3. Add on the negative slack to the clock period target, clear the current design data, and re-synthesize. This is expected to meet timing
4. Report results. If timing is violated again, add on negative slack. If not, increment the clock period target by `delay_increment` (default is 0.5ns, will need to be scaled accordingly for larger designs. There is room for more intelligent logic to select this clock period target)
5. Continue the loop of synthesizing -> checking reports -> clearing design data until minimum area has saturated (the design area has not decreased for three iterations)
6. Exit after completing pareto curve generation

### Generated Reports

- `area.rpt`
- `power.rpts`
- `qor.rpt`
- `resources.rpts`
- `timing.rpt` 

## Pareto Curve Plotting

The `plot_synthesis_results.py` script generates Pareto curves from synthesis results. This tool visualizes the trade-offs between area, delay, and power for different design implementations.

### Usage

```bash
python plot_synthesis_results.py [OPTIONS]
```

### Required Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--input_dir` | `-i` | Path to directory containing synthesis results for different designs |
| `--design_config` | `-d` | Path to YAML config file with different designs to be plotted |
| `--output_dir` | `-o` | Path to output directory where plots will be saved |
| `--module_name` | `-m` | Name of the top module of the design |
| `--title` | `-t` | Title of the plot |

### Optional Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--remove_points` | `-r` | Remove non-Pareto optimal points from graph |
| `--power` | `-p` | Use power as X-axis instead of area |

### Example Usage

#### Basic Pareto Curve Generation
```bash
python plot_synthesis_results.py \
    --input_dir ./designs \
    --design_config ./design_config.yaml \
    --output_dir ./plots \
    --module_name adder_brent_kung_64b \
    --title "Brent-Kung 64-bit Adder Pareto Curve"
```

#### Power vs Delay Analysis
```bash
python plot_synthesis_results.py \
    --input_dir ./designs \
    --design_config ./design_config.yaml \
    --output_dir ./plots \
    --module_name adder_brent_kung_64b \
    --title "Brent-Kung 64-bit Adder Power-Delay Analysis" \
    --power
```

#### Clean Pareto Curve (Optimal Points Only)
```bash
python plot_synthesis_results.py \
    --input_dir ./designs \
    --design_config ./design_config.yaml \
    --output_dir ./plots \
    --module_name adder_brent_kung_64b \
    --title "Brent-Kung 64-bit Adder Pareto Curve Optimal Points" \
    --remove_points
```

### Design Configuration File

The `design_config.yaml` file should contain the directory names for the different designs to be plotted. Example structure:

```yaml
designs:
  - adder_brent_kung_64b
  - adder_sklansky_64b
  - adder_ripple_carry_64b
```

### Output

The script generates:
- **Pareto curve plots** showing Area vs Delay or Power vs Delay tradeoffs
- **JSON data file** containing raw extracted metrics
