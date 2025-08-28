##########################################################################################
# Copyright (c) 2024 Synopsys, Inc. All rights reserved.
##########################################################################################

set_clock_uncertainty 0.2 [get_clocks clk]
#set_clock_latency -early 0.50 [get_clocks clk]
#set_clock_latency -late  0.55 [get_clocks clk]
set_clock_latency -min 0.50 [get_clocks clk]
set_clock_latency -max 0.55 [get_clocks clk]
set_clock_transition 0.2 [get_clocks clk]

set_input_delay -clock [get_clocks clk] 0.5 ${input_ports}
set_output_delay -clock [get_clocks clk] 0.6 ${output_ports}

#set_input_delay -clock [get_clocks v_ate_clk] 0 ${input_test_ports}
#set_output_delay -clock [get_clocks v_ate_clk] 0 ${output_test_ports}

#set_driving_cell -lib_cell ${DRIVING_CELL_CLOCKS} ${clock_ports}
#set_driving_cell -lib_cell ${DRIVING_CELL_PORTS} ${input_ports}
#set_driving_cell -lib_cell ${DRIVING_CELL_PORTS} ${input_test_ports}

set_max_transition 0.15 -clock_path [get_clocks clk]
