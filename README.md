# RTLA Synthesis Environment

A synthesis environment configured for Synopsys RTL Architect (RTLA) using a 32nm Synopsys PDK with design corner analysis. Tailored for the purpose of pareto curve generation.

## Overview

This repository contains the complete synthesis setup for digital circuit design using Synopsys RTL Architect. It provides automated synthesis flows, timing analysis, and design optimization capabilities across multiple process corners. Additionally, it contains scripting to generate pareto curve plots and analyze PPA design tradeoffs.

## Configured Design Corners

The synthesis environment is configured for the following four design corners:

1. **FF1p16125c**: Short path delay, highest leakage current
2. **FF1p1640c**: Shortest path delays, worst-case for hold timing, higher switching power, lower leakage
3. **SS0p95v125c**: Longest path delays, worst-case for setup timing, higher leakage
4. **SS0p95v40c**: Long path delays, low leakage

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

## Quick Start

### Basic Synthesis Flow

1. **Prepare your RTL design**:
   ```bash
   # Place your Verilog/VHDL files in the designs/ directory
   cp your_design.v designs/
   ```

2. **Configure synthesis parameters**:
   ```bash
   # Edit the synthesis configuration file
   vim config/synthesis_config.tcl
   ```

3. **Run synthesis**:
   ```bash
   python run_synthesis.py --design your_design --corner TT
   ```

4. **Analyze results**:
   ```bash
   python analyze_results.py --design your_design
   ```

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

## Configuration

### Synthesis Configuration

The main synthesis configuration is in `config/synthesis_config.tcl`:

```tcl
# Key parameters
set CLOCK_PERIOD 10.0
set TARGET_LIBRARY "your_library.db"
set LINK_LIBRARY "* $TARGET_LIBRARY"
set SEARCH_PATH "path/to/libraries"
```

### Design Configuration

Design-specific settings are in `config/design_config.yaml`:

```yaml
designs:
  - name: "your_design"
    top_module: "top_module_name"
    clock_periods: [5.0, 10.0, 15.0, 20.0]
    optimization_goals: ["area", "power", "timing"]
```

## Pareto Curve Generation

### Generated Reports

- **area.rpt**:
- **power.rpts**:
- **qor.rpt**: 
- **resources.rpts**:
- **timing.rpt**: 

## Pareto Curve Plotting

