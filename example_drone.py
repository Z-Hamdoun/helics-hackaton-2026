"""
References:
    - https://mavlink.io/en/mavgen_python/
    - https://ardupilot.org/dev/docs/copter-commands-in-guided-mode.html
"""

import time
from pymavlink import mavutil


class MiniMAVLinCS:
    """Classe permettant de communiquer en mavlink avec une FC"""

    def __init__(self, address: str, baud: int = 115200):
        """Ouvre la connexion et attend le premier heartbeat.

        Args:
            address (str): adresse de connexion, ex. "udpin:127.0.0.1:14550".
            baud (int): baudrate.
        """
        self.master = mavutil.mavlink_connection(address, baud=baud)

        self.master.wait_heartbeat()

    def _wait_ack(self, command: int, timeout: float = 3) -> bool:
        """Attend le COMMAND_ACK d'une commande précise.

        Args:
            command (int): identifiant MAV_CMD_... de la commande envoyée.
            timeout (float): temps max d'attente en secondes.

        Returns:
            bool: True si la commande a été acceptée (MAV_RESULT_ACCEPTED).
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = self.master.recv_match(
                type="COMMAND_ACK", blocking=True, timeout=deadline - time.time()
            )
            if msg is None:
                return False
            if msg.command == command:
                return msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED
            time.sleep(0.05)
        return False

    def change_mode(self, mode: str, timeout: float = 3) -> bool:
        """Change le mode de vol (ex: "GUIDED", "LAND", "RTL").
        """
        mode_id = self.master.mode_mapping()[mode.upper()]
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            0,  # confirmation
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_ENABLED,
            mode_id,  # param2 : numéro du mode (GUIDED, LAND, ...)
            0, 0, 0, 0, 0,  # param3-7 
        )
        return self._wait_ack(mavutil.mavlink.MAV_CMD_DO_SET_MODE, timeout=timeout)

    def arm(self, timeout: float = 3) -> bool:
        """Arme les moteurs."""
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            1,  # param1 : 1 = arm, 0 = disarm
            0, 0, 0, 0, 0, 0,  # param2-7 (inutilisés)
        )
        return self._wait_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=timeout)

    def disarm(self, timeout: float = 3) -> bool:
        """Désarme les moteurs."""
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,  # confirmation
            0,  # param1 : 0 = disarm
            0, 0, 0, 0, 0, 0,
        )
        return self._wait_ack(mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, timeout=timeout)

    def takeoff(self, altitude: float, timeout: float = 3) -> bool:
        """Décolle jusqu'à `altitude` mètres (relatif au sol).
        """
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0,  # confirmation
            0, 0, 0, 0,  # param1-4 
            0, 0,  # param5-6 : latitude/longitude (0 = position actuelle)
            altitude,  # param7 : altitude relative en mètres
        )
        return self._wait_ack(mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, timeout=timeout)

    def goto(self, lat: float, lon: float, alt: float) -> None:
        """Envoie le drone vers un point GPS (mode GUIDED requis).
        Args:
            lat (float): latitude en degrés.
            lon (float): longitude en degrés.
            alt (float): altitude relative au décollage, en mètres.
        """
        self.master.mav.set_position_target_global_int_send(
            0,  # time_boot_ms (ignoré par ArduPilot)
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            0b0000111111111000,  # type_mask, n'active que la position x/y/z
            int(lat * 1e7),
            int(lon * 1e7),
            alt,
            0, 0, 0,  # vx, vy, vz
            0, 0, 0,  # afx, afy, afz
            0, 0,     # yaw, yaw_rate
        )

    def land(self, timeout: float = 3) -> bool:
        """Fait atterrir le drone là où il se trouve (passage en mode LAND)."""
        return self.change_mode("LAND", timeout=timeout)

    def close(self) -> None:
        """Ferme la connexion."""
        self.master.close()


if __name__ == "__main__":
    # Exemple d'utilisation (simulation SITL) :
    drone = MiniMAVLinCS("udpin:127.0.0.1:14550")

    print("Mode GUIDED :", drone.change_mode("GUIDED"))
    print("Armement :", drone.arm())
    print("Décollage :", drone.takeoff(5))

    time.sleep(10)
    drone.goto(-35.3630, 149.1652, 5)  # exemple

    time.sleep(10)
    print("Atterrissage :", drone.land())

    drone.close()
