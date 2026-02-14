import socket
import time
import statistics
from enum import Enum

# enum to hold tcp reno state
class State(Enum):
    SLOW_START = 1
    CONGESTION_AVOIDANCE = 2
    FAST_RECOVERY = 3


udp_ip = "localhost"
sender_port = 3000
receiver_port = 5001

PACKET_SIZE = 1024
SEQ_ID_SIZE = 4
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

# tcp reno vars
cwnd = 1 * MESSAGE_SIZE            
ssthresh = 64 * MESSAGE_SIZE
dup_ack_count = 0
state = State.SLOW_START

send_base = 0 # lowest unacked byte
next_seq = 0 # next byte to send

# RTT tracking
send_times = {}
rtt_values = []

# create socker
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sender.bind((udp_ip, sender_port))
sender.settimeout(1)

throughput_start = time.time()

def create_packet(seq_id, payload):
    return int.to_bytes(seq_id, SEQ_ID_SIZE, signed=True, byteorder='big') + payload


# read in file
message = b''
with open("./docker/file.mp3", "rb") as f:
    message = f.read()

message_len = len(message)



while send_base < message_len:

    while next_seq < send_base + cwnd and next_seq < message_len:

        chunk = message[next_seq:next_seq + MESSAGE_SIZE]
        sender.sendto(create_packet(next_seq, chunk), (udp_ip, receiver_port))

        send_times[next_seq] = time.time()
        next_seq += len(chunk)

    try:
        packet, _ = sender.recvfrom(PACKET_SIZE)
        ack_id = int.from_bytes(packet[:SEQ_ID_SIZE], signed=True, byteorder='big')
        ack_flag = packet[SEQ_ID_SIZE:]

        if ack_flag != b'ack':
            continue

        # new ack
        if ack_id > send_base:

            dup_ack_count = 0

            # RTT sample
            if send_base in send_times:
                rtt_values.append(time.time() - send_times[send_base])

            bytes_acked = ack_id - send_base
            send_base = ack_id

            # state shifting
            if state == State.SLOW_START:
                cwnd += bytes_acked # effective doubling of cwnd
                if cwnd >= ssthresh:
                    state = State.CONGESTION_AVOIDANCE

            elif state == State.CONGESTION_AVOIDANCE:
                cwnd += MESSAGE_SIZE * (bytes_acked / cwnd)

            elif state == State.FAST_RECOVERY:
                cwnd = ssthresh
                state = State.CONGESTION_AVOIDANCE

            # print(f"[ACK] state={state}, cwnd={round(cwnd/MESSAGE_SIZE,2)} MSS")

        # dup ack
        elif ack_id == send_base:

            dup_ack_count += 1

            if dup_ack_count == 3:
                # print("[FAST RETRANSMIT]")

                ssthresh = max(cwnd / 2, MESSAGE_SIZE)
                cwnd = ssthresh + 3 * MESSAGE_SIZE
                state = State.FAST_RECOVERY

                # retransmit missing segment
                chunk = message[send_base:send_base + MESSAGE_SIZE]
                sender.sendto(create_packet(send_base, chunk), (udp_ip, receiver_port))

            elif state == State.FAST_RECOVERY:
                cwnd += MESSAGE_SIZE

            # print(f"[DUP ACK] state={state}, cwnd={round(cwnd/MESSAGE_SIZE,2)} MSS")

    except socket.timeout:

        # print("[TIMEOUT]")

        ssthresh = max(cwnd / 2, MESSAGE_SIZE)
        cwnd = MESSAGE_SIZE
        state = State.SLOW_START
        dup_ack_count = 0

        next_seq = send_base  # retransmit from base


finished = False
while not finished:
    try:
        sender.sendto(create_packet(send_base, b''), (udp_ip, receiver_port))
        packet, _ = sender.recvfrom(PACKET_SIZE)
        ack = packet[SEQ_ID_SIZE:]
        if ack == b'fin':
            sender.sendto(create_packet(send_base, b'==FINACK=='), (udp_ip, receiver_port))
            finished = True
    except socket.timeout:
        continue

# performance calculations
throughput_end = time.time()
throughput = throughput_end - throughput_start
avg_rtt = statistics.mean(rtt_values) if rtt_values else 0

performance = 0.3 * throughput / 1000 + 0.7 / avg_rtt if avg_rtt > 0 else 0

print(f"{throughput:.7f}, {avg_rtt:.7f}, {performance:.7f}")

sender.close()
