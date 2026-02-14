import socket
import time
import statistics

udp_ip = "localhost"
sender_port = 3000
receiver_port = 5001

sender_addr = (udp_ip, sender_port)
receiver_addr = (udp_ip, receiver_port)

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
WINDOW_SIZE = 100

throughput_start = time.time()
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender.bind(sender_addr)
sender.settimeout(1)

def create_packet(seq_id, payload):
    return int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big') + payload

curr_seq_id = 0
message_array = []
ppd_start = []
ppd_end = []
ppd_array = []

with open("docker/file.mp3", "rb") as file:
    buf = file.read(MESSAGE_SIZE)
    while (buf):
        message_array.append(buf)
        buf = file.read(MESSAGE_SIZE)
        
last_ack_index = -1
last_sent_index = last_ack_index
window_index = WINDOW_SIZE

last_ack_flag = False
finished_flag = False

while not last_ack_flag:           
    while last_sent_index < window_index:
        last_sent_index += 1
        
        if last_sent_index == len(message_array):
            sender.sendto(create_packet(curr_seq_id, b''), receiver_addr)
        else: 
            sender.sendto(create_packet(last_sent_index * MESSAGE_SIZE, message_array[last_sent_index]), receiver_addr)
            
            if last_sent_index == len(ppd_start):
                ppd_start.append(time.time())
        
    while True:
        try:
            packet, _ = sender.recvfrom(PACKET_SIZE)
            next_seq_id, ack = packet[:SEQ_ID_SIZE], packet[SEQ_ID_SIZE:]
                
            next_seq_id = int.from_bytes(next_seq_id, signed=True, byteorder='big')
            
            if next_seq_id > curr_seq_id and ack == b'ack':
                pack_acks = (next_seq_id - curr_seq_id) // MESSAGE_SIZE
                last_ack_index += pack_acks
                window_index += pack_acks
                
                end_time = time.time()
                
                i = 0
                while i < pack_acks:
                    ppd_end.append(end_time)
                    i += 1
                
                if (next_seq_id - curr_seq_id) % MESSAGE_SIZE != 0:
                    last_ack_index += 1
                    window_index += 1
                    ppd_end.append(end_time)
                
                curr_seq_id = next_seq_id
                    
                if window_index > len(message_array):
                    window_index = len(message_array)
                    
                while last_sent_index < window_index:
                    last_sent_index += 1
                    ppd_start.append(time.time())
                    
                    # print(last_sent_index, "packet sent")
                    
                    if last_sent_index == len(message_array):
                        sender.sendto(create_packet(curr_seq_id, b''), receiver_addr)
                    else:
                        sender.sendto(create_packet(last_sent_index * MESSAGE_SIZE, message_array[last_sent_index]), receiver_addr)
                
            elif last_ack_index + 1 == len(message_array) and ack == b'ack' and not last_ack_flag:
                last_ack_flag = True
                throughput_end = time.time()
                
        except socket.timeout:
            last_sent_index = last_ack_index
            break
        
while not finished_flag:
    try:
        sender.sendto(create_packet(curr_seq_id, b''), receiver_addr)
        packet, _ = sender.recvfrom(PACKET_SIZE)
        _, ack = packet[:SEQ_ID_SIZE], packet[SEQ_ID_SIZE:]
        
        if ack == b'fin':
            sender.sendto(create_packet(curr_seq_id, b'==FINACK=='), receiver_addr)
            finished_flag = True
            
    except socket.timeout:
        continue
            
throughput = throughput_end - throughput_start

for i in range(len(ppd_end)):
    ppd_array.append(ppd_end[i] - ppd_start[i])
ppd_avg = statistics.mean(ppd_array)

performance = 0.3 * throughput / 1000 + 0.7 / ppd_avg

print(f"{throughput:0.7f}, {ppd_avg:0.7f}, {performance:0.7f}")

sender.close()