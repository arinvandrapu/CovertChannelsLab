#!/usr/bin/env python3
"""
Covert Timing Channel - Sender

Encodes message bits using inter-arrival time (IAT) delays.
- Bit 0: shorter delay (default 0.1s)
- Bit 1: longer delay (default 0.2s)

Optionally logs the sent IATs for analysis.
"""

import socket
import time
import argparse


def text_to_bits(text):
    """Convert ASCII text to binary string"""
    return ''.join(format(ord(c), '08b') for c in text)


def send_timing_channel(target_ip, target_port, message, bit0_delay, bit1_delay, log_file=None):
    """Send message by encoding bits in packet timing"""
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bits = text_to_bits(message)
    
    print(f"Target: {target_ip}:{target_port}")
    print(f"Message: {message}")
    print(f"Length: {len(message)} chars ({len(bits)} bits)")
    print(f"Delays: bit0={bit0_delay}s, bit1={bit1_delay}s")
    print(f"Gap: {abs(bit1_delay - bit0_delay) * 1000:.1f}ms")
    
    log = None
    if log_file:
        log = open(log_file, 'w')
        log.write("bit_idx,bit,iat\n")
        print(f"Logging to: {log_file}")
    
    print(f"\nTransmitting {len(bits)} bits...\n")
    
    start_time = time.time()
    
    for i, bit in enumerate(bits):
        sock.sendto(b'X', (target_ip, target_port))
        
        if bit == '0':
            delay = bit0_delay
        else:
            delay = bit1_delay
        
        if log:
            log.write(f"{i},{bit},{delay}\n")
        
        time.sleep(delay)
        
        if (i + 1) % 80 == 0:
            print(f"Sent {i+1}/{len(bits)} bits")
    
    # EOF markers
    print("Sending EOF markers...")
    for _ in range(3):
        sock.sendto(b'EOF', (target_ip, target_port))
        time.sleep(0.5)
    
    elapsed = time.time() - start_time
    bps = len(bits) / elapsed if elapsed > 0 else 0
    
    print(f"\nDone: {len(bits)} bits in {elapsed:.2f}s ({bps:.1f} bits/sec)")
    
    if log:
        log.close()
    sock.close()


def main():
    parser = argparse.ArgumentParser(
        description='Covert Timing Channel Sender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python timing_sender.py --target 127.0.0.1 --port 9999
  python timing_sender.py --target 127.0.0.1 --port 9999 --bit0_delay 0.05 --bit1_delay 0.10
  python timing_sender.py --log sent_iats.csv
        """
    )
    
    parser.add_argument('--target', default='127.0.0.1', help='Receiver IP')
    parser.add_argument('--port', type=int, default=9999, help='Receiver port')
    parser.add_argument('--bit0_delay', type=float, default=0.1, help='Delay for bit 0 (sec)')
    parser.add_argument('--bit1_delay', type=float, default=0.2, help='Delay for bit 1 (sec)')
    parser.add_argument('--message', default="Help! I need somebody. Help! Not just anybody.",
                       help='Message to send')
    parser.add_argument('--log', default=None, help='Log sent IATs to CSV')
    
    args = parser.parse_args()
    
    send_timing_channel(args.target, args.port, args.message,
                       args.bit0_delay, args.bit1_delay, args.log)


if __name__ == '__main__':
    main()
