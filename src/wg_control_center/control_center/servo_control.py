import threading
import time

import RPi.GPIO as GPIO


class ServoController:
    def __init__(self, pin: int = 20, frequency: int = 50):
        self.pin = pin
        self.frequency = frequency
        self.center_angle = 90
        self.sweep_offset = 15
        self.step_delay = 0.02
        self._running = threading.Event()
        self._stop_requested = threading.Event()
        self._worker = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self._pwm = GPIO.PWM(self.pin, self.frequency)
        self._pwm.start(0)
        self.set_angle(self.center_angle)

    def angle_to_duty_cycle(self, angle: float) -> float:
        angle = max(0.0, min(180.0, float(angle)))
        return 2.5 + (angle / 18.0)

    def set_angle(self, angle: float) -> None:
        self._pwm.ChangeDutyCycle(self.angle_to_duty_cycle(angle))
        time.sleep(0.2)

    def _sweep_loop(self) -> None:
        low = self.center_angle - self.sweep_offset
        high = self.center_angle + self.sweep_offset

        while not self._stop_requested.is_set():
            for angle in range(low, high + 1):
                if self._stop_requested.is_set():
                    break
                self.set_angle(angle)
                time.sleep(self.step_delay)

            for angle in range(high, low - 1, -1):
                if self._stop_requested.is_set():
                    break
                self.set_angle(angle)
                time.sleep(self.step_delay)

        self.set_angle(self.center_angle)
        self._running.clear()

    def run(self) -> None:
        if self._running.is_set():
            print("Servo sweep already running")
            return

        self._stop_requested.clear()
        self._running.set()
        self._worker = threading.Thread(target=self._sweep_loop, daemon=True)
        self._worker.start()
        print("Servo sweep started")

    def stop(self) -> None:
        if not self._running.is_set():
            self.set_angle(self.center_angle)
            print("Servo centered at 90")
            return

        self._stop_requested.set()
        if self._worker is not None:
            self._worker.join(timeout=2.0)
        self.set_angle(self.center_angle)
        print("Servo centered at 90")

    def close(self) -> None:
        self.stop()
        self._pwm.stop()
        GPIO.cleanup(self.pin)


def main() -> None:
    controller = ServoController(pin=20)
    print("Type 'run' to sweep 90 +/- 15 degrees, 'stop' to center the servo, or 'exit' to quit.")

    try:
        while True:
            command = input("> ").strip().lower()
            if command == "run":
                controller.run()
            elif command == "stop":
                controller.stop()
            elif command in {"exit", "quit"}:
                break
            elif command:
                print("Unknown command. Use run, stop, or exit.")
    except KeyboardInterrupt:
        pass
    finally:
        controller.close()


if __name__ == "__main__":
    main()