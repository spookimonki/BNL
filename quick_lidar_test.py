#!/usr/bin/env python3
"""Quick test of LiDAR auto-detection using updated code logic."""

import glob
import os
import serial

def find_lidar_port():
    """Auto-detect LiDAR serial port - matches lidar_relay.py logic."""
    ports_to_try = [
        '/dev/serial0',
        '/dev/ttyAMA0',
        '/dev/ttyS0',
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
    ]
    ports_to_try.extend(glob.glob('/dev/ttyUSB*'))
    
    print("Searching for available serial ports...")
    for port in ports_to_try:
        if os.path.exists(port):
            print(f"✓ Found: {port}")
            return port
    
    print("✗ No serial ports found")
    return None

def test_lidar(port):
    """Try to connect and read LiDAR data."""
    print(f"\nTesting connection to {port}...")
    try:
        ser = serial.Serial(port, 230400, timeout=1.0)
        print(f"✓ Opened {port}")
        
        data = ser.read(100)
        ser.close()
        
        if data:
            print(f"✓ Received {len(data)} bytes")
            if 0x54 in data:
                print("✓ LD06 LiDAR DETECTED! ✓✓✓")
                print(f"  First bytes: {data[:10].hex()}")
                return True
            else:
                print("✗ Data received but not LD06 format")
        else:
            print("✗ No data received")
    except PermissionError:
        print(f"✗ Permission denied - try: sudo chmod 666 {port}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return False

if __name__ == '__main__':
    print("="*60)
    print("LD06 LiDAR Auto-Detection Test")
    print("="*60)
    
    port = find_lidar_port()
    if port:
        test_lidar(port)
    else:
        print("\n⚠️  No serial ports available!")
        print("Solutions:")
        print("1. Reboot: sudo reboot")
        print("2. Or connect LiDAR via USB-to-serial adapter")
    
    print("\n" + "="*60)
