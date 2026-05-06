#!/usr/bin/env python3
"""Quick LiDAR connectivity test."""

import serial
import time

print("Testing LD06 LiDAR connection on /dev/serial0...")
try:
    ser = serial.Serial('/dev/serial0', 230400, timeout=1.0)
    print("✓ Serial port opened successfully")
    
    # Try to read data
    print("Waiting for LiDAR data...")
    data = ser.read(100)
    
    if data:
        print(f"✓ Received {len(data)} bytes from LiDAR")
        print(f"  First bytes (hex): {data[:10].hex()}")
        # LD06 packets start with 0x54
        if data[0] == 0x54 or 0x54 in data:
            print("✓ Valid LD06 packet header (0x54) detected!")
        else:
            print("✗ No valid packet header found - check pin connections")
    else:
        print("✗ No data received - LiDAR may not be connected or powered")
    
    ser.close()
except FileNotFoundError:
    print("✗ /dev/serial0 not found - serial port may not be enabled")
    print("  Run: sudo raspi-config → Interface → Serial Port")
except Exception as e:
    print(f"✗ Error: {e}")
