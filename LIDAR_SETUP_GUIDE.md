# LD06 LiDAR Serial Connection - SOLUTION GUIDE

## Problem Identified
✓ UART is **ENABLED** in `/boot/firmware/config.txt`
✗ But `/dev/ttyAMA0` or `/dev/serial0` device **does NOT exist**

This happens because device tree changes require a system reboot to take effect.

---

## SOLUTION - Choose Option A or B

### **OPTION A: Reboot (Recommended - Official GPIO pins)**
This will create `/dev/ttyAMA0` for the official Raspberry Pi UART pins 8/10.

```bash
sudo reboot
```

After reboot:
1. Connect LiDAR to GPIO pins:
   - Pin 8 (GPIO14/TX) → Keep connected
   - Pin 10 (GPIO15/RX) ← LiDAR Tx wire
   - Pin 6 or 9 (GND) → LiDAR GND
   - Pin 2 or 4 (5V) → LiDAR +5V

2. Verify serial device exists:
```bash
ls -la /dev/ttyAMA0
```

3. Launch LiDAR node:
```bash
cd /home/bnluser/Desktop/Elias_BNL
source install/setup.bash
ros2 launch wg_bringup wg.launch.py mode:=real
```

4. Verify LiDAR is publishing:
```bash
ros2 topic echo /scan
```

---

### **OPTION B: Use USB Serial Adapter (If reboot not possible)**
If you have a CP2102 or CH340 USB-to-serial adapter:

1. Connect adapter to Raspberry Pi USB port
2. Connect LiDAR to adapter:
   - Adapter RX → LiDAR Tx
   - Adapter TX → LiDAR RX (if it has one)
   - Adapter GND → LiDAR GND
   - Adapter 5V → LiDAR +5V

3. Verify adapter shows up:
```bash
ls /dev/ttyUSB*
```

4. Test connection:
```bash
cd /home/bnluser/Desktop/Elias_BNL
python3 lidar_test.py
```

5. If adapter shows as `/dev/ttyUSB0`, run LiDAR node:
```bash
source install/setup.bash
ros2 launch wg_bringup wg.launch.py mode:=real
```

The node will **auto-detect** the serial port! ✓

---

## What I've Already Done

✅ Modified `/home/bnluser/Desktop/Elias_BNL/src/wg_sensor_pullup/elias_relay/lidar_relay.py` to:
- Auto-detect available serial ports
- Try `/dev/serial0`, `/dev/ttyAMA0`, `/dev/ttyS0`, and `/dev/ttyUSB*` in order
- Log detailed error messages if connection fails
- Provide helpful troubleshooting info

✅ Created diagnostic tool: `lidar_diagnostic.py`

---

## Verification Checklist

After connecting LiDAR and rebooting (or using USB adapter):

- [ ] LiDAR has power (LED indicator should be on)
- [ ] Serial port exists: `ls /dev/ttyAMA0` or `ls /dev/ttyUSB0`
- [ ] LiDAR data detected: `python3 lidar_test.py`
- [ ] ROS2 node running: `ros2 node list`
- [ ] Scans publishing: `ros2 topic list | grep scan`
- [ ] View scan data: `ros2 topic echo /scan`

---

## Quick Reboot Command

```bash
sudo reboot
```

System will reboot. SSH/reconnect and test after ~30 seconds.
