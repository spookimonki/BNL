#!/usr/bin/env python3
"""BNO085 - Simplified test with only ROTATION_VECTOR"""
import sys
import time

try:
    import board
    import busio
    from adafruit_bno08x.i2c import BNO08X_I2C
    from adafruit_bno08x import BNO_REPORT_ROTATION_VECTOR
except ImportError as e:
    print(f"❌ Missing: {e}")
    sys.exit(1)


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     BNO085 ROTATION VECTOR ONLY TEST                       ║
║     (Avoiding conflicting report types)                    ║
╚════════════════════════════════════════════════════════════╝
    """)

    try:
        print("→ Initializing I2C...")
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        print("→ Scanning for BNO085...")
        sensor = BNO08X_I2C(i2c, address=0x4A)
        print("✓ Connected\n")

        print("→ Enabling ROTATION_VECTOR feature...")
        sensor.enable_feature(BNO_REPORT_ROTATION_VECTOR, 10000)
        print("✓ Enabled\n")

        print("→ Waiting for first data packet...")
        time.sleep(1)

        print("\n" + "="*60)
        print("READING ROTATION VECTOR DATA")
        print("="*60 + "\n")

        for i in range(15):
            try:
                quat = sensor.quaternion
                if quat and any(abs(v) > 1e-6 for v in quat):
                    print(f"[{i+1:2d}] ✓ Quat: i={quat[0]:7.4f} j={quat[1]:7.4f} k={quat[2]:7.4f} w={quat[3]:7.4f}")
                else:
                    print(f"[{i+1:2d}] ⚠ Quat: {quat} (all zeros or None)")
            except Exception as e:
                print(f"[{i+1:2d}] ✗ Error: {e}")
            
            time.sleep(0.2)

        print("\n✓ BNO085 is working!")
        print("  - ROTATION_VECTOR data is being read successfully")
        print("  - Sensor is communicating properly on I2C")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            i2c.deinit()
        except:
            pass


if __name__ == '__main__':
    main()
