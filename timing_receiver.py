#!/usr/bin/env python3
"""
Covert Timing Channel - Receiver

Decodes message from inter-arrival time (IAT) of incoming packets.
Compares each IAT to a threshold to determine each bit.

Logs received IATs for SNR analysis and statistical evaluation.
"""

import socket
import time
import argparse
import math


def receive_timing_channel(listen_port, threshold=0.15, log_file=None):
    """Receive and decode timing channel, optionally logging IATs"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', listen_port))
    
    print(f"Listening on port {listen_port}")
    print(f"Threshold: {threshold}s")
    print(f"Waiting for packets...\n")
    
    bits = []
    iats = []
    bit_labels = []
    
    prev_time = None
    start_time = None
    eof_count = 0
    packets_received = 0
    
    log = None
    if log_file:
        log = open(log_file, 'w')
        log.write("bit_idx,bit,iat\n")
    
    while True:
        data, addr = sock.recvfrom(1024)
        current_time = time.time()
        packets_received += 1
        
        # EOF check
        if data == b'EOF':
            eof_count += 1
            if eof_count >= 2:
                break
            continue
        
        # First packet starts the clock
        if start_time is None:
            start_time = current_time
            prev_time = current_time
            continue
        
        # Calculate IAT
        iat = current_time - prev_time
        iats.append(iat)
        
        # Decode bit
        bit = '1' if iat > threshold else '0'
        bits.append(bit)
        bit_labels.append(bit)
        
        # Log to file
        if log:
            log.write(f"{len(bits)-1},{bit},{iat}\n")
        
        prev_time = current_time
        
        if len(bits) % 80 == 0:
            print(f"Decoded {len(bits)} bits...")
    
    # Convert bits to text
    bits_str = ''.join(bits)
    chars = [bits_str[i:i+8] for i in range(0, len(bits_str), 8)]
    message = ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)
    
    elapsed = time.time() - start_time
    bps = len(bits) / elapsed if elapsed > 0 else 0
    
    # Compute statistics 
    iats_0 = [iats[i] for i in range(len(iats)) if bit_labels[i] == '0']
    iats_1 = [iats[i] for i in range(len(iats)) if bit_labels[i] == '1']
    
    mean_0 = sum(iats_0) / len(iats_0) if iats_0 else 0
    mean_1 = sum(iats_1) / len(iats_1) if iats_1 else 0
    
    var_0 = sum((x - mean_0) ** 2 for x in iats_0) / len(iats_0) if iats_0 else 0
    var_1 = sum((x - mean_1) ** 2 for x in iats_1) / len(iats_1) if iats_1 else 0
    
    std_0 = math.sqrt(var_0)
    std_1 = math.sqrt(var_1)
    
    
    print(f"\n{'='*60}")
    print(f"Reception complete")
    print(f"{'='*60}")
    print(f"\nMessage: \"{message}\"")
    print(f"Bits: {len(bits)}")
    print(f"Packets: {packets_received}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Rate: {bps:.1f} bits/sec")
    
    print(f"\nIAT Statistics")
    print(f"Bit 0: mean={mean_0:.4f}s, std={std_0:.4f}s ({len(iats_0)} samples)")
    print(f"Bit 1: mean={mean_1:.4f}s, std={std_1:.4f}s ({len(iats_1)} samples)")
    
    print(f"{'='*60}\n")
    
    if log:
        log.close()
        print(f"IATs logged to: {log_file}")
    
    sock.close()


def main():
    parser = argparse.ArgumentParser(
        description='Covert Timing Channel Receiver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python timing_receiver.py --port 9999 --threshold 0.15
  python timing_receiver.py --port 9999 --threshold 0.15 --log iats.csv

The --log option saves all received IATs (bit index, decoded bit, measured IAT)
for analysis and SNR calculation in Jupyter.
        """
    )
    
    parser.add_argument('--port', type=int, default=9999, help='Listen port')
    parser.add_argument('--threshold', type=float, default=0.15,
                       help='IAT threshold for bit discrimination (sec)')
    parser.add_argument('--log', default=None, help='Log IATs to CSV')
    
    args = parser.parse_args()
    
    receive_timing_channel(args.port, args.threshold, args.log)


if __name__ == '__main__':
    main()
