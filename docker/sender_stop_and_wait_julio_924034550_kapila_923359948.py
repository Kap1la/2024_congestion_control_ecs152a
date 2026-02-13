import socket
import time
import statistics

udp_ip = "localhost"
sender_port = 2000
receiver_port = 5001

sender_addr = (udp_ip, sender_port)
receiver_addr = (udp_ip, receiver_port)

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
throughput_start = time.time()

sender.bind(sender_addr)
sender.settimeout(1)

def create_packet(seq_id, payload):
    return int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big') + payload

curr_seq_id = 0
message_array = []
ppd_array = []

with open("docker/file.mp3", "rb") as file:
    buf = file.read(MESSAGE_SIZE)
    while (buf):
        message_array.append(buf)
        buf = file.read(MESSAGE_SIZE)
        
i = 0
start_time_flag = True
last_ack = False

while True:
    try:
        if i == len(message_array):
            sender.sendto(create_packet(curr_seq_id, b''), receiver_addr)
        else:
            sender.sendto(create_packet(curr_seq_id, message_array[i]), receiver_addr)
            
            if start_time_flag:
                ppd_start = time.time()
                start_time_flag = False
        
        packet, _ = sender.recvfrom(PACKET_SIZE)
        next_seq_id, ack = packet[:SEQ_ID_SIZE], packet[SEQ_ID_SIZE:]
        
        next_seq_id = int.from_bytes(next_seq_id, signed=True, byteorder='big')
        # print("Next seq id received is: ", next_seq_id)
        
        if next_seq_id > curr_seq_id and ack == b'ack':
            i += 1
            curr_seq_id = next_seq_id

            print(i, " packets delivered")
            ppd_end = time.time()
            ppd = ppd_end - ppd_start
            ppd_array.append(ppd)
            start_time_flag = True
            
        elif i == len(message_array) and ack == b'ack':
                # print("This happened first")
                last_ack = True
                throughput_end = time.time()

        elif ack == b'fin' and last_ack:
            # print("This happens second")
            sender.sendto(create_packet(curr_seq_id, b'==FINACK=='), receiver_addr)
            break
        else:
            # print("repeat") - never happened
            continue
        
    except socket.timeout:
        # print("timeout")
        continue

throughput = throughput_end - throughput_start
ppd_avg = statistics.mean(ppd_array)
performance = 0.3 * throughput / 1000 + 0.7 / ppd_avg

print(f"{throughput:0.7f}, {ppd_avg:0.7f}, {performance:0.7f}")