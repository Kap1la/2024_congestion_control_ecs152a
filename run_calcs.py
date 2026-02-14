import statistics

# Stop And Wait
saw_throughput = [966.2888401,968.6239021,995.1880946,961.8505008,987.2919190,1009.3388352,976.3835568,998.8854973,959.4354711,987.4859211]
saw_ppd_avg = [0.1850152,0.1854684,0.1905691,0.1841576,0.1890042,0.1932499,0.1869321,0.1912448,0.1836857,0.1890804]
saw_performance = [4.0733598,4.0648159,3.9717639,4.0896465,3.9998085,3.9250546,4.0375894,3.9598949,4.0986871,3.9983756]

saw_throughput_avg = statistics.mean(saw_throughput)
saw_throughput_sd = statistics.stdev(saw_throughput)
saw_ppd_avg_avg = statistics.mean(saw_ppd_avg)
saw_ppd_avg_sd = statistics.stdev(saw_ppd_avg)
saw_performance_avg = statistics.mean(saw_performance)
saw_performance_sd = statistics.stdev(saw_performance)
print(f"{saw_throughput_avg:.7},{saw_throughput_sd:.7},{saw_ppd_avg_avg:.7},{saw_ppd_avg_sd:.7},{saw_performance_avg:.7},{saw_performance_sd:.7}")

# Fixed Sliding Window
fsw_throughput = [60.6123371,59.0753055,60.5363166,60.8001311,59.8971214,59.9257832,56.6331890,59.3523180,56.3041368,62.4335487]
fsw_ppd_avg = [1.1695556,1.1315740,1.1604177,1.1732120,1.1494228,1.1559196,1.0925058,1.1428399,1.0502570,1.1837174]
fsw_performance = [0.6167016,0.6363299,0.6213920,0.6148926,0.6269705,0.6235562,0.6577188,0.6303149,0.6833948,0.6100874]

fsw_throughput_avg = statistics.mean(fsw_throughput)
fsw_throughput_sd = statistics.stdev(fsw_throughput)
fsw_ppd_avg_avg = statistics.mean(fsw_ppd_avg)
fsw_ppd_avg_sd = statistics.stdev(fsw_ppd_avg)
fsw_performance_avg = statistics.mean(fsw_performance)
fsw_performance_sd = statistics.stdev(fsw_performance)
print(f"{fsw_throughput_avg:.7},{fsw_throughput_sd:.7},{fsw_ppd_avg_avg:.7},{fsw_ppd_avg_sd:.7},{fsw_performance_avg:.7},{fsw_performance_sd:.7}")

# TCP Reno
reno_throughput = [59.1265697,61.1773221,59.1042626,57.1225247,58.7858531,59.2988043,56.0382938,54.3050275,53.5749304,53.0045104]
reno_rtt_avg = [0.7553030,1.1591652,1.1045337,1.0244642,1.1175969,0.7791407,0.9978592,0.9937882,0.9653215,0.9617490]
reno_performance = [0.9445183,0.6222361,0.6514829,0.7004207,0.6439797,0.9162153,0.7183132,0.7206669,0.7412195,0.7437420]

reno_throughput_avg = statistics.mean(reno_throughput)
reno_throughput_sd = statistics.stdev(reno_throughput)
reno_rtt_avg_avg = statistics.mean(reno_rtt_avg)
reno_rtt_avg_sd = statistics.stdev(reno_rtt_avg)
reno_performance_avg = statistics.mean(reno_performance)
reno_performance_sd = statistics.stdev(reno_performance)
print(f"{reno_throughput_avg:.7},{reno_throughput_sd:.7},{reno_rtt_avg_avg:.7},{reno_rtt_avg_sd:.7},{reno_performance_avg:.7},{reno_performance_sd:.7}")