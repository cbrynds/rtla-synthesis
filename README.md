# RTLA Synthesis Environment

A synthesis environment configured for Synopsys RTL Architect (RTLA) using a 32nm Synopsys PDK with design corner analysis. Tailored for the purpose of pareto curve generation.

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

### Basic Synthesis Flow (WIP)

1. **Prepare your RTL design**:

2. **Configure synthesis constraints**:

3. **Run synthesis**:

4. **Analyze results**:

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

### Design Configuration

## Pareto Curve Generation

### Generated Reports

- **area.rpt**:
- **power.rpts**:
- **qor.rpt**: 
- **resources.rpts**:
- **timing.rpt**: 

## Pareto Curve Plotting

