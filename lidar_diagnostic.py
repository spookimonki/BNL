#!/usr/bin/env python3
"""LD06 LiDAR and Raspberry Pi Serial Port Diagnostic Tool"""

import os
import glob
import subprocess
import serial
from pathlib import Path


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_uart_config():
    """Check /boot/firmware/config.txt for UART settings"""
    print_section("1. UART Configuration")
    
    config_paths = [
        '/boot/firmware/config.txt',
        '/boot/config.txt',
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"✓ Found config at: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'enable_uart=1' in content:
                        print("✓ UART is ENABLED (enable_uart=1)")
                    else:
                        print("✗ UART is NOT enabled - Add 'enable_uart=1' to config")
                    
                    # Check for relevant dtoverlays
                    if 'dwc2' in content or 'vc4-kms' in content:
                        print(f"  Found USB/Video overlays: {[line.strip() for line in content.split('\n') if 'dtoverlay' in line]}")
            except PermissionError:
                print(f"✗ Permission denied reading {config_path} (try: sudo)")
            return
    
    print("✗ Config file not found at expected locations")


def check_serial_devices():
    """Check what serial devices are available"""
    print_section("2. Available Serial Devices")
    
    # Check common device paths
    devices_to_check = [
        '/dev/serial0',
        '/dev/ttyAMA0',
        '/dev/ttyS0',
        '/dev/ttyUSB*',
    ]
    
    found_devices = []
    for pattern in devices_to_check:
        if '*' in pattern:
            devices = glob.glob(pattern)
            found_devices.extend(devices)
        elif os.path.exists(pattern):
            found_devices.append(pattern)
    
    if found_devices:
        print(f"✓ Found serial devices:")
        for dev in sorted(found_devices):
            try:
                stat_info = os.stat(dev)
                print(f"  - {dev} (mode: {oct(stat_info.st_mode)[-3:]})")
            except OSError as e:
                print(f"  - {dev} (error: {e})")
    else:
        print("✗ No serial devices found!")
        print("  Actions to try:")
        print("  1. sudo raspi-config → Interface Options → Serial Port → Enable")
        print("  2. Reboot: sudo reboot")
        print("  3. Or connect LiDAR via USB-to-serial adapter (will show as /dev/ttyUSB0)")


def check_device_permissions():
    """Check permissions on serial devices"""
    print_section("3. Serial Device Permissions")
    
    for pattern in ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0', '/dev/ttyUSB*']:
        devices = glob.glob(pattern) if '*' in pattern else [pattern] if os.path.exists(pattern) else []
        
        for dev in devices:
            try:
                stat_info = os.stat(dev)
                is_readable = bool(stat_info.st_mode & 0o100)
                is_writable = bool(stat_info.st_mode & 0o200)
                
                if is_readable and is_writable:
                    print(f"✓ {dev}: Readable & Writable")
                else:
                    print(f"✗ {dev}: {'R' if is_readable else 'r'}{'W' if is_writable else 'w'}")
                    print(f"  Fix with: sudo chmod 666 {dev}")
            except OSError:
                pass


def test_serial_connection():
    """Try to open serial ports and detect LiDAR data"""
    print_section("4. Serial Connection Test")
    
    # Find first available port
    ports_to_try = glob.glob('/dev/ttyUSB*') + ['/dev/serial0', '/dev/ttyAMA0', '/dev/ttyS0']
    
    if not ports_to_try:
        print("✗ No serial ports available to test")
        return
    
    for port in ports_to_try:
        if not os.path.exists(port):
            continue
            
        print(f"\nTrying {port}...")
        try:
            ser = serial.Serial(port, 230400, timeout=1.0)
            print(f"  ✓ Opened {port}")
            
            # Try to read data
            data = ser.read(100)
            ser.close()
            
            if data:
                print(f"  ✓ Received {len(data)} bytes")
                # Check for LD06 packet header (0x54)
                if 0x54 in data:
                    print(f"  ✓ Found LD06 packet header (0x54)!")
                    print(f"  ✓ LD06 LiDAR DETECTED on {port}")
                    return
                else:
                    print(f"  ✗ Data received but no LD06 header found")
                    print(f"    First bytes (hex): {data[:20].hex()}")
            else:
                print(f"  ✗ No data received")
        except PermissionError:
            print(f"  ✗ Permission denied - try: sudo chmod 666 {port}")
        except serial.SerialException as e:
            print(f"  ✗ Error: {e}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
    
    print("\n✗ LiDAR not detected on any port")
    print("  Check:")
    print("  1. LiDAR is powered (should have LED indicator)")
    print("  2. TX/RX pins are not swapped")
    print("  3. Ground is connected")
    print("  4. Baud rate is 230400")


def main():
    print("\n" + "="*60)
    print("  LD06 LiDAR & Raspberry Pi UART Diagnostics")
    print("  Created for troubleshooting serial connection issues")
    print("="*60)
    
    try:
        check_uart_config()
        check_serial_devices()
        check_device_permissions()
        test_serial_connection()
    except Exception as e:
        print(f"\n✗ Diagnostic error: {e}")
    
    print("\n" + "="*60)
    print("  Diagnostic Complete")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
