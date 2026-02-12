"""
Covert Storage Channel - Receiver

Decodes message from IP_ID field of raw IP packets.
Filters by source IP, destination IP, and TTL value.

Requires: sudo python storage_receiver.py [options]
"""

import argparse
import time
from scapy.all import sniff, IP, conf

conf.verb = 0


class StorageChannelReceiver:
    """Receives and decodes covert storage channel messages"""
    
    def __init__(self, source_ip='127.0.0.1', dest_ip='127.0.0.1', ttl=42, debug=False):
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.expected_ttl = ttl
        self.debug = debug
        self.decoded_bytes = []
        self.start_time = None
        self.bytes_per_packet = 2  # IP_ID is 16 bits
        self.eof_threshold = 0xFFFF
        self.packet_count = 0
        self.last_packet_id = None
        self.system_packets_filtered = 0
    
    def packet_callback(self, pkt):
        """Process incoming packet and extract covert data"""
        
        if IP not in pkt:
            return
        
        encoded_value = pkt[IP].id
        ttl = pkt[IP].ttl
        
        # Filter by TTL to eliminate system packets
        if ttl != self.expected_ttl:
            self.system_packets_filtered += 1
            if self.debug:
                print(f"[TTL] skip 0x{encoded_value:04x} (TTL {ttl} != {self.expected_ttl})")
            return
        
        # Skip duplicate packets (loopback quirk)
        if encoded_value == self.last_packet_id:
            if self.debug:
                print(f"[DUP] skip 0x{encoded_value:04x}")
            return
        
        self.last_packet_id = encoded_value
        
        # Start timer on first valid packet
        if self.start_time is None:
            self.start_time = time.time()
            print(f"Started at {time.strftime('%H:%M:%S')}\n")
        
        # Check for EOF
        if encoded_value == self.eof_threshold:
            print("\nEOF detected - transmission complete")
            return
        
        # Decode bytes
        byte_list = []
        
        if self.debug:
            print(f"\n[Pkt {self.packet_count + 1}] 0x{encoded_value:04x}")
        
        for i in range(self.bytes_per_packet - 1, -1, -1):
            byte_val = (encoded_value >> (i * 8)) & 0xFF
            
            if self.debug:
                char = chr(byte_val) if 32 <= byte_val <= 126 else f"0x{byte_val:02x}"
                print(f"  byte {i}: 0x{byte_val:02x} ({byte_val:3d}) '{char}'", end="")
            
            if byte_val == 0:
                if self.debug:
                    print(" [null]")
                break
            
            if 32 <= byte_val <= 126:
                byte_list.append(chr(byte_val))
                if self.debug:
                    print(" [ok]")
            else:
                if self.debug:
                    print(" [skip]")
        
        self.decoded_bytes.extend(byte_list)
        self.packet_count += 1
        
        current_msg = ''.join(self.decoded_bytes)
        print(f"Pkt {self.packet_count}: {len(self.decoded_bytes)} chars: '{current_msg}'")
    
    def run(self):
        """Start sniffing for packets"""
        print(f"Receiver (debug={self.debug})")
        print(f"Source: {self.source_ip}")
        print(f"Dest: {self.dest_ip}")
        print(f"TTL: {self.expected_ttl}")
        print(f"Waiting...\n")
        
        try:
            filter_str = f"ip src {self.source_ip} and ip dst {self.dest_ip}"
            sniff(
                prn=self.packet_callback,
                filter=filter_str,
                store=False,
                iface="lo"
            )
        except KeyboardInterrupt:
            print("\n\nInterrupted")
            self.print_results()
        except PermissionError:
            print("\nError: requires root (use: sudo python storage_receiver.py ...)")
            self.print_results()
        except Exception as e:
            print(f"\nError: {e}")
            self.print_results()
    
    def print_results(self):
        """Print decoded message and statistics"""
        message = ''.join(self.decoded_bytes)
        
        print(f"\n{'='*60}")
        print(f"Results")
        print(f"{'='*60}")
        
        if self.start_time is None:
            print("No packets received")
            return
        
        elapsed = time.time() - self.start_time
        bits_decoded = len(self.decoded_bytes) * 8
        bps = bits_decoded / elapsed if elapsed > 0 else 0
        
        print(f"\nMessage: \"{message}\"")
        print(f"Length: {len(self.decoded_bytes)} chars")
        print(f"Packets: {self.packet_count}")
        print(f"Filtered: {self.system_packets_filtered} system packets")
        print(f"Time: {elapsed:.3f}s")
        print(f"Rate: {bps:.1f} bits/sec")
        
        print(f"\n{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Covert Storage Channel Receiver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  sudo python storage_receiver.py --ttl 42
  sudo python storage_receiver.py --ttl 42 --debug
  sudo python storage_receiver.py --source 127.0.0.1 --dest 127.0.0.1 --ttl 42
        """
    )
    
    parser.add_argument('--source', default='127.0.0.1', help='Source IP filter')
    parser.add_argument('--dest', default='127.0.0.1', help='Destination IP filter')
    parser.add_argument('--ttl', type=int, default=42, help='Expected TTL value')
    parser.add_argument('--debug', action='store_true', help='Show per-packet details')
    
    args = parser.parse_args()
    
    receiver = StorageChannelReceiver(args.source, args.dest, args.ttl, args.debug)
    receiver.run()


if __name__ == '__main__':
    main()
