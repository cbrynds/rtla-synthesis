# Directory Variables
set scripts_dir "./scripts/"

# set DESIGN_NAME	  <top module name>
set DESIGN_LIBRARY	  ${DESIGN_NAME}.dlib

# Pareto Synthesis Variables
set low_bound 0.01
set high_bound 100.0
set epsilon 0.01
set max_iterations 20
set num_pareto_points 10

# Return the WNS from a timing report
proc check_violation {filename} {
    set fp [open $filename r]
    set result 0
    while {[gets $fp line] >= 0} {
        if {[regexp {VIOLATED} $line]} {
            # Split the line and find the value (assuming it's the last word)
            set words [split $line]
            set result [lindex $words end]
            close $fp
            return $result
        }
    }
    close $fp
    return 0
}

proc timing_met {report_file} {
    set fp [open $report_file r]
    set content [read $fp]
    close $fp
    # Check for no "VIOLATED" or slack > 0 (adjust regex)
    if {[regexp {slack.*MET} $content]} {
        return 1
    } else {
        return 0
    }
}

# Return the combinational area from an area report
proc get_combinational_area {filename} {
    set fp [open $filename r]
    set area 0
    while {[gets $fp line] >= 0} {
        if {[regexp {^Combinational area:\s+([0-9.]+)} $line match value]} {
            set area $value
            break
        }
    }
    close $fp
    return $area
}

proc report_synthesis_results {clock_target report_dir} {
    if {![file exists "${report_dir}/${clock_target}"]} {
        file mkdir "${report_dir}/${clock_target}"
    }

    # Report Design Metrics
    report_timing > "${report_dir}/${clock_target}/timing.rpt"
    report_qor > "${report_dir}/${clock_target}/qor.rpt"
    report_area > "${report_dir}/${clock_target}/area.rpt"
    report_resources > "${report_dir}/${clock_target}/resources.rpt"
    report_power > "${report_dir}/${clock_target}/power.rpt"
}

proc find_min_area {} {
    global ENDPOINTS_DIR low_bound high_bound epsilon max_iterations clock_period_target
    set tightest $high_bound

    set clock_period_target $high_bound
    source "${scripts_dir}/run_synthesis.tcl"
    report_synthesis_results $clock_period_target $ENDPOINTS_DIR
    set min_area [get_combinational_area "$ENDPOINTS_DIR/$clock_period_target/area.rpt"]

    reset_design
    remove_block
    remove_design -all

    for {set i 0} {$i < $max_iterations} {incr i} {
        set mid [expr {($low_bound + $high_bound) / 2.0}]
        puts "Testing area at $mid ns..."
        set clock_period_target $mid

        source "${scripts_dir}/run_synthesis.tcl"
        report_synthesis_results $clock_period_target $ENDPOINTS_DIR
        set design_area [get_combinational_area "$ENDPOINTS_DIR/$clock_period_target/area.rpt"]

        if {$design_area <= [expr {$min_area + $epsilon}]} {
            set tightest $mid
            set high $mid
        } else {
            set low $mid
        }

        if {abs($high_bound - $low_bound) < $epsilon} break

        reset_design
        remove_block
        remove_design -all
    }
    puts "Minimum area of $min_area um^2 found at clock period $tightest ns."
    return $tightest
}

proc find_min_delay {min_area_timing_constraint} {
    global ENDPOINTS_DIR low_bound high_bound epsilon max_iterations clock_period_target

    set min_delay_constraint $min_area_timing_constraint

    for {set i 0} {$i < $max_iterations} {incr i} {
        set mid [expr ($low_bound + $high_bound) / 2.0]
        puts "Testing delay at $mid ns..."
        source "${scripts_dir}/run_synthesis.tcl"

        report_synthesis_results $mid $ENDPOINTS_DIR
        set timing_met [timing_met "$ENDPOINTS_DIR/$clock_period_target/timing.rpt"]

        if {$timing_met} {
            set min_delay_constraint $mid
            set high $mid
        } else {
            set low $mid
        }
        if {abs($high_bound - $low_bound) < 0.001} break

        reset_design
        remove_block
        remove_design -all
    }
    return $min_delay_constraint
}

proc compute_delay_targets {min_area_timing_constraint min_delay_timing_constraint} {
    global num_pareto_points
    set delay_targets {}
    set delay_increment [expr {($min_area_timing_constraint - $min_delay_timing_constraint) / ($num_pareto_points - 1)}]
    for {set i 0} {$i < $num_pareto_points} {incr i} {
        lappend delay_targets [expr {$min_area_timing_constraint + $i * $delay_increment}]
    }
    return $delay_targets
}

#################################################################################
# Main Script Setup
#################################################################################

source -echo "$scripts_dir/setup.tcl"

set ENDPOINTS_DIR "${REPORTS_DIR}/endpoints"
if [file exists ${ENDPOINTS_DIR}]  {
  file delete -force ${ENDPOINTS_DIR}
}
file mkdir $ENDPOINTS_DIR

#################################################################################
# Find minimum area and minimum delay endpoints and compute Pareto points
#################################################################################

# Find min delay and min area points
puts "Determining minimimum achievable area of the design..."
set min_area_timing_constraint [find_min_area]

puts "Determining minimum achievable delay of design..."
set min_delay_timing_constraint [find_min_delay $min_area_timing_constraint]

puts "Determining ${num_pareto_points} Pareto points between $min_area_timing_constraint ns and $min_delay_timing_constraint ns."
set delay_targets [compute_delay_targets $min_area_timing_constraint $min_delay_timing_constraint]

#################################################################################
# Evaluate Pareto points
#################################################################################

puts "Evaluating delay targets: $delay_targets"
for {set i 0} {$i < [llength $delay_targets]} {incr i} {
    set clock_period_target [lindex $delay_targets $i]
    puts "Synthesizing for target clock period: $clock_period_target ps"

    source "${scripts_dir}/run_synthesis.tcl"

    report_synthesis_results $clock_period_target $REPORTS_DIR

    reset_design
    remove_block
    remove_design -all
}

# exit
