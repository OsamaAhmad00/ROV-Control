#!/bin/bash
gpu=$(/opt/vc/bin/vcgencmd measure_temp)
gpu=${gpu:5}
gpu=${gpu::(-4)}
echo $gpu
