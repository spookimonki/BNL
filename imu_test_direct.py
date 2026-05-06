#!/usr/bin/env python3
"""Direct BNO08X IMU test on I2C - No ROS2"""
import sys
import time

try:
    import board
    import busio
    from adafruit_bno08x.i2c import BNO08X_I2C
    from adafruit_bno08x import (
        BNO_REPORT_ACCELEROMETER,
        BNO_REPORT_GYROSCOPE,
        BNO_REPORT_ROTATION_VECTOR,
    )
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install with: pip3 install adafruit-circuitpython-bno08x")
    sys.exit(1)


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║         DIRECT IMU TEST (No ROS2)                          ║
║  I2C Bus: 1, Address: 0x4A (BNO08X)                       ║
║  Pins: SDA=GPIO2, SCL=GPIO3                               ║
╚════════════════════════════════════════════════════════════╝
    """)

    try:
        print("→ Initializing I2C bus 1...")
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
        print("✓ I2C bus initialized")

        print("→ Scanning for BNO08X at address 0x4A...")
        sensor = BNO08X_I2C(i2c, address=0x4A)
        print("✓ BNO08X found and initialized")

        # Try reset first
        print("→ Attempting sensor reset...")
        try:
            sensor.reset()
            time.sleep(1)
            print("✓ Sensor reset complete")
        except Exception as e:
            print(f"⚠ Reset not available: {e}")

        # Enable sensor reports
        report_interval_us = 10000  # 100 Hz
        print(f"→ Enabling sensor reports (100 Hz)...")
        try:
            sensor.enable_feature(BNO_REPORT_ROTATION_VECTOR, report_interval_us)
            sensor.enable_feature(BNO_REPORT_ACCELEROMETER, report_interval_us)
            sensor.enable_feature(BNO_REPORT_GYROSCOPE, report_interval_us)
            print("✓ Sensor reports enabled")
        except KeyError as e:
            print(f"⚠ Invalid report ID from sensor: {e}")
            print("  Sensor may need hardware reset or firmware update")
            print("  Attempting to read raw quaternion anyway...")
        except Exception as e:
            print(f"⚠ Error enabling features: {e}")

        print("\n" + "="*60)
        print("READING IMU DATA (10 samples)")
        print("="*60)

        for i in range(10):
            try:
                # Try to read each sensor safely
                quat = sensor.quaternion if hasattr(sensor, 'quaternion') else None
                accel = sensor.linear_acceleration if hasattr(sensor, 'linear_acceleration') else None
                gyro = sensor.gyro if hasattr(sensor, 'gyro') else None

                print(f"\n[Sample {i+1}]")
                
                if quat:
                    quat_i, quat_j, quat_k, quat_real = quat
                    print(f"  ✓ Quaternion: i={quat_i:.4f}, j={quat_j:.4f}, k={quat_k:.4f}, w={quat_real:.4f}")
                else:
                    print(f"  ✗ Quaternion: unavailable")
                
                if accel:
                    accel_x, accel_y, accel_z = accel
                    print(f"  ✓ Accel (m/s²): x={accel_x:.3f}, y={accel_y:.3f}, z={accel_z:.3f}")
                else:
                    print(f"  ✗ Accel: unavailable")
                
                if gyro:
                    gyro_x, gyro_y, gyro_z = gyro
                    print(f"  ✓ Gyro (rad/s): x={gyro_x:.3f}, y={gyro_y:.3f}, z={gyro_z:.3f}")
                else:
                    print(f"  ✗ Gyro: unavailable")

                time.sleep(0.1)
            except Exception as e:
                print(f"  ❌ Read error: {e}")
                time.sleep(0.1)

        if quat or accel or gyro:
            print("\n✓ IMU test complete - sensor is communicating!")
        else:
            print("\n⚠ IMU initialized but not responding to data requests")

    except FileNotFoundError as e:
        print(f"❌ I2C bus error: {e}")
        print("   Make sure I2C is enabled: i2cdetect -y 1")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        try:
            i2c.deinit()
            print("\n✓ I2C cleaned up")
        except:
            pass


if __name__ == '__main__':
    main()
