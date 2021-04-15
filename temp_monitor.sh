#!/bin/bash
cpu=$(</sys/class/thermal/thermal_zone0/temp)
gpu=$(/opt/vc/bin/vcgencmd measure_temp)
gpu=${gpu:5}
gpu=${gpu::(-2)}
echo "GPU: $gpu"
echo "CPU: $((cpu/1000)) ($cpu/1000)"
