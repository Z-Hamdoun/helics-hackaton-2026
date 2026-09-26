#!/usr/bin/python3
"""
picamera2_new.py

A drop-in replacement for the Picamera2 library that integrates Gazebo camera 
transport directly into the Picamera2 class without requiring gzcam.py.
"""

import logging
import time
import numpy as np
from PIL import Image

try:
    from gz.transport13 import Node
    from gz.msgs10.image_pb2 import Image as GzImage
    _GZ_AVAILABLE = True
except ImportError:
    _GZ_AVAILABLE = False

_log = logging.getLogger("picamera2_new")

RESOLUTION_CAMERA_GAZEBO: tuple[int, int] = (848, 480)

CAMERA_MATRIX_GAZEBO = np.array(
    [
        [205.4696273803711, 0.0, 320.0],
        [0.0, 205.4696559906006, 240.0],
        [0.0, 0.0, 1.0],
    ],
    dtype=np.float64,
)

DIST_COEFFS_GAZEBO = np.array([0.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float64)


class Picamera2:
    """Drop-in replacement for Picamera2 using direct Gazebo transport integration."""

    # Mimic common Picamera2 / logging constants
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self, camera_num=0, verbose_console=None, tuning=None, allocator=None):
        _log.info("Initializing Picamera2 with direct Gazebo backend...")

        self.__resolution: tuple[int, int] = RESOLUTION_CAMERA_GAZEBO
        self.__frame: np.ndarray | None = None
        self.__node = None

        self.camera_matrix: np.ndarray = CAMERA_MATRIX_GAZEBO
        self.dist_coeffs: np.ndarray = DIST_COEFFS_GAZEBO

        if _GZ_AVAILABLE:
            try:
                camera_topic: str = "/world/iris_runway/model/iris_with_gimbal/model/gimbal/link/pitch_link/sensor/camera/image"
                self.__node = Node()
                subscribed = self.__node.subscribe(GzImage, camera_topic, self.__image_callback)
                if not subscribed:
                    _log.error(f"Failed to subscribe to Gazebo topic: {camera_topic}")
            except Exception as e:
                _log.error(f"Error initializing Gazebo transport Node: {e}")
        else:
            _log.warning("gz.transport13 not available; running in dummy mode.")

        self._running = False
        self._configuration = {}

    @property
    def resolution(self) -> tuple[int, int]:
        return self.__resolution

    def __image_callback(self, msg) -> None:
        try:
            width = msg.width
            height = msg.height
            data = msg.data
            self.__resolution = (width, height)
            self.__frame = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
        except Exception:
            self.__frame = None

    def __get_frame(self, timeout: float = 0.5) -> np.ndarray:
        if self.__frame is not None:
            return self.__frame

        start_time = time.time()
        while self.__frame is None:
            if time.time() - start_time > timeout:
                return np.zeros((self.__resolution[1], self.__resolution[0], 3), dtype=np.uint8)
            time.sleep(0.01)

        return self.__frame

    @staticmethod
    def set_logging(level=logging.WARN, output=None, msg=None):
        log = logging.getLogger("picamera2_new")
        if level is not None:
            log.setLevel(level)

    @staticmethod
    def load_tuning_file(tuning_file, dir=None):
        return {}

    def configure(self, camera_config=None):
        _log.info("Configuring camera (stubbed for Gazebo)...")
        if camera_config is not None:
            self._configuration = camera_config

    def start(self, config=None, show_preview=False):
        if config is not None:
            self.configure(config)
        self._running = True
        _log.info("Camera started (Gazebo backend).")

    def stop(self):
        self._running = False
        _log.info("Camera stopped (Gazebo backend).")

    def close(self):
        self.stop()
        _log.info("Camera closed.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def start_preview(self, preview=None, **kwargs):
        _log.info("start_preview called (no-op in Gazebo backend).")

    def stop_preview(self):
        _log.info("stop_preview called (no-op in Gazebo backend).")

    def attach_preview(self, preview):
        pass

    def detach_preview(self):
        pass

    def set_controls(self, controls):
        _log.info(f"set_controls called with {controls} (no-op in Gazebo backend).")

    def capture_array(self, name="main", wait=None, signal_function=None) -> np.ndarray:
        return self.__get_frame()

    def capture_buffer(self, name="main", wait=None, signal_function=None) -> np.ndarray:
        return self.__get_frame()

    def capture_image(self, name="main", wait=None, signal_function=None) -> Image.Image:
        arr = self.__get_frame()
        return Image.fromarray(arr)

    def capture_file(self, filename, name="main", format=None, exif_data=None, wait=None, signal_function=None):
        img = self.capture_image(name=name)
        img.save(filename, format=format)

    def capture_metadata(self, wait=None, signal_function=None) -> dict:
        return {"FrameDuration": 33333330, "SensorTimestamp": 0}

    # Configuration creators (stubs returning empty dicts so calls don't crash)
    def create_preview_configuration(self, *args, **kwargs):
        return {}

    def create_still_configuration(self, *args, **kwargs):
        return {}

    def create_video_configuration(self, *args, **kwargs):
        return {}
