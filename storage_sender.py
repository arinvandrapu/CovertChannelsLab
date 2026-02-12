"""
Covert Storage Channel - Sender

Encodes a message into the IP_ID field of raw IP packets.
Uses custom TTL value to distinguish channel packets from system packets.

Requires: sudo python storage_sender.py [options]
"""

import argparse
import time
from scapy.all import IP, send, conf

conf.verb = 0


def send_storage_channel(target_ip, message, ttl=42, verbose=True):
    """
    Send message by encoding into IP_ID field.
    
    Args:
        target_ip: Destination IP address
        message: Message to transmit
        ttl: TTL value to use (default: 42)
        verbose: Print status output
    """
    
    bytes_per_packet = 2  # IP_ID is 16 bits
    
    if verbose:
        print(f"Target: {target_ip}")
        print(f"Message: '{message}'")
        print(f"Length: {len(message)} bytes")
        packets_needed = (len(message) + bytes_per_packet - 1) // bytes_per_packet
        print(f"Packets: {packets_needed}\n")
    
    start_time = time.time()
    packets_sent = 0
    
    # Encode message into packets
    for i in range(0, len(message), bytes_per_packet):
        chunk = message[i:i+bytes_per_packet]
        chunk = chunk.ljust(bytes_per_packet, '\x00')
        
        # Convert bytes to 16-bit integer
        encoded_value = 0
        for char in chunk:
            encoded_value = (encoded_value << 8) | ord(char)
        
        pkt = IP(dst=target_ip, id=encoded_value, ttl=ttl)
        
        if verbose:
            chunk_display = chunk.rstrip('\x00') if chunk != '\x00' * bytes_per_packet else "(pad)"
            print(f"Pkt {packets_sent + 1}: '{chunk_display}' → 0x{encoded_value:04x}")
        
        try:
            send(pkt, verbose=0)
            packets_sent += 1
            time.sleep(0.05)
        except Exception as e:
            print(f"Error sending packet: {e}")
            return
    
    # Send EOF markers
    if verbose:
        print("\nSending EOF markers...")
    
    for _ in range(3):
        eof_pkt = IP(dst=target_ip, id=0xFFFF, ttl=ttl)
        try:
            send(eof_pkt, verbose=0)
            time.sleep(0.05)
        except:
            pass
    
    elapsed = time.time() - start_time
    bps = (len(message) * 8) / elapsed if elapsed > 0 else 0
    
    if verbose:
        print(f"\nSent {packets_sent} packets in {elapsed:.3f}s ({bps:.1f} bits/sec)")


def main():
    parser = argparse.ArgumentParser(
        description='Covert Storage Channel Sender',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python storage_sender.py --target 127.0.0.1
  sudo python storage_sender.py --target 127.0.0.1 --ttl 99
  sudo python storage_sender.py --target 192.168.1.5 --message "Secret"
        """
    )
    
    parser.add_argument('--target', default='127.0.0.1', help='Receiver IP address')
    parser.add_argument('--message', default="Help! I need somebody. Help! Not just anybody.",
                       help='Message to transmit')
    parser.add_argument('--ttl', type=int, default=42, help='TTL value (default: 42)')
    
    args = parser.parse_args()
    
    send_storage_channel(args.target, args.message, args.ttl)


if __name__ == '__main__':
    main()
