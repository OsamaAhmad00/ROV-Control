argc=$#

max_cpu_temp=1000
if [ $argc -ge 1 ]; then
	max_cpu_temp=$1
fi

max_gpu_temp=$max_cpu_temp
if [ $argc -ge 2 ]; then
	max_gpu_temp=$2
fi

cpu_temp=$(./cpu_temp.sh)
gpu_temp=$(./gpu_temp.sh)

echo "Argc: $argc"
echo "CPU Limit: $max_cpu_temp"
echo "GPU Limit: $max_gpu_temp"
echo "CPU: $cpu_temp"
echo "GPU: $gpu_temp"

if [ $cpu_temp -gt $max_cpu_temp ] || [ $gpu_temp -gt $max_gpu_temp ]; then
	shutdown -P now
fi
