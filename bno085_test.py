#!/usr/bin/env python3
"""BNO085 IMU Direct Test - Detailed initialization with proper timing"""
import sys
import time

try:
    import board
    import busio
    from adafruit_bno08x.i2c import BNO08X_I2C
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip3 install adafruit-circuitpython-bno08x")
    sys.exit(1)


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║       BNO085 IMU INITIALIZATION TEST                       ║
║  I2C Bus: 1, Address: 0x4A                                ║
╚════════════════════════════════════════════════════════════╝
    """)

    try:
        print("→ Initializing I2C bus...")
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        print("✓ I2C initialized\n")

        print("→ Scanning for BNO085 at 0x4A...")
        sensor = BNO08X_I2C(i2c, address=0x4A)
        print("✓ BNO085 detected\n")

        print("→ Device boot-up delay (2 seconds)...")
        time.sleep(2)
        print("✓ Delay complete\n")

        # Try to read sensor info
        print("="*60)
        print("SENSOR INFORMATION")
        print("="*60)
        
        try:
            print(f"✓ Sensor initialized (no errors on probe)")
        except Exception as e:
            print(f"⚠ Error: {e}")

        # Try simple property reads without enabling features
        print("\n" + "="*60)
        print("ATTEMPTING TO READ SENSOR DATA")
        print("="*60)

        for attempt in range(5):
            print(f"\n[Attempt {attempt + 1}]")
            try:
                # Try to read quaternion (might be available by default)
                quat = sensor.quaternion
                if quat and any(quat):  # Check if not all zeros
                    print(f"✓ Quaternion: {quat}")
                else:
                    print(f"⚠ Quaternion all zeros or None: {quat}")
            except Exception as e:
                print(f"✗ Quaternion read failed: {e}")

            try:
                # Try to read acceleration
                accel = sensor.linear_acceleration
                if accel and any(accel):
                    print(f"✓ Acceleration: {accel}")
                else:
                    print(f"⚠ Acceleration all zeros or None: {accel}")
            except Exception as e:
                print(f"✗ Acceleration read failed: {e}")

            time.sleep(0.5)

        print("\n" + "="*60)
        print("FEATURE ENABLE TEST")
        print("="*60)

        # List available report types
        from adafruit_bno08x import (
            BNO_REPORT_ROTATION_VECTOR,
            BNO_REPORT_ACCELEROMETER,
            BNO_REPORT_GYROSCOPE,
        )

        reports = [
            ("ROTATION_VECTOR", BNO_REPORT_ROTATION_VECTOR),
            ("ACCELEROMETER", BNO_REPORT_ACCELEROMETER),
            ("GYROSCOPE", BNO_REPORT_GYROSCOPE),
        ]

        for name, report_id in reports:
            print(f"\n→ Enabling {name} (ID: {report_id})...")
            try:
                sensor.enable_feature(report_id, 10000)
                print(f"  ✓ {name} enabled")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                print(f"     Continuing anyway...")

        print("\n" + "="*60)
        print("FINAL DATA READ")
        print("="*60)

        for i in range(3):
            print(f"\n[Sample {i+1}]")
            try:
                q = sensor.quaternion
                a = sensor.linear_acceleration
                g = sensor.gyro
                print(f"  Quat: {q}")
                print(f"  Accel: {a}")
                print(f"  Gyro: {g}")
            except Exception as e:
                print(f"  Error: {e}")
            time.sleep(0.5)

        print("\n✓ Test complete")

    except FileNotFoundError as e:
        print(f"❌ I2C bus error: {e}")
        sys.exit(1)
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
