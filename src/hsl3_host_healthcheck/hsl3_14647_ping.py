import socket
import time
from typing import Dict

def udp_packet_ping(host: str, logger: object, port: int = 7, timeout: float = 2.0) -> Dict:
    """
    Probe a UDP port without raw sockets or elevated privileges.

    Args:
        host: The hostname or IP address to check
        port: UDP port to probe, preferably one expected to be closed (default: 7)
        timeout: Timeout in seconds (default: 4)

    Returns:
        A dictionary with keys "available", "response_ms", and "status" indicating the result of the UDP probe.
        - "available": True if a UDP reply or port-unreachable error is received, False otherwise.
        - "response_ms": The round-trip time in milliseconds, or None if unavailable.
        - "status": A string describing the result, e.g., "connected", "connection_refused", "timeout", or "os_error".
    """
    start = time.monotonic()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.send(b'\x00')
            sock.recv(4096)

            logger.info("UDP probe to %s:%s succeeded", host, port)  # type: ignore
            return {
                "available": True,
                "response_ms": round(
                    (time.monotonic() - start) * 1000, 2
                ),
                "status": "connected"
            }
    except ConnectionRefusedError as exc:
        logger.info("UDP probe to %s:%s succeeded: %s", host, port, exc)  # type: ignore
        return {"available": True, "response_ms": round((time.monotonic() - start) * 1000, 2), "status": "connection_refused"}
    except socket.timeout as exc:
        logger.error("UDP probe to %s:%s failed: %s", host, port, exc)  # type: ignore
        return {"available": False, "response_ms": None, "status": f"timeout: {str(exc)}"}
    except OSError as exc:
        logger.error("UDP probe to %s:%s failed: %s", host, port, exc)  # type: ignore
        return {"available": False, "response_ms": None, "status": f"os_error: {str(exc)}"}


def tcp_health_check(host: str, port: int,  logger: object, timeout: float = 4) -> Dict:
    """
    Execute a TCP health check to verify if a host is reachable on a specific port.
    
    Args:
        host: The hostname or IP address to check
        port: The port number to connect to
        timeout: Timeout in seconds (default: 4)
        logger: Optional logger object for logging errors and info messages
    
    Returns:
        A dictionary with keys "available", "response_ms", and "status" indicating the result of the TCP health check.
    Warning:
        - A successful TCP connection does not guarantee that the host is fully operational.
        - Network conditions may affect the results.
    """
    
    start = time.monotonic()        
    try:
        with socket.create_connection((host, port), timeout=timeout):
            logger.info(f"TCP health check succeeded: connection to {host}:{port} was established")  # type: ignore
                
            return {
                "available": True,
                "response_ms": round(
                    (time.monotonic() - start) * 1000, 2
                ),
                "status": "connected"
            }
               
    except ConnectionRefusedError:
        logger.error(f"TCP health check failed: connection to {host}:{port} was refused")  # type: ignore
        return {"available": False, "response_ms": None, "status": "connection_refused"}
        
    except socket.timeout:
        logger.error(f"TCP health check failed: hostname {host} could not be resolved due to timeout")  # type: ignore
        return { "available": False, "response_ms": None, "status": "timeout" }

    except OSError as exc:
        logger.error(f"TCP health check failed: {str(exc)}")  # type: ignore
        return { "available": False, "response_ms": None, "status": str(exc) }
    

def wake_on_lan(mac_address: str, hostname: str, logger: object, port: int = 9) -> bool:
    """
    Send a Wake-on-LAN magic packet to a host.

    Args:
        mac_address: The MAC address of the target host (e.g., "AA:BB:CC:DD:EE:FF")
        hostname: The hostname of the target host (used to determine the broadcast address)
        port: The UDP port to send the packet to (default: 9)

    Returns:
        True if the magic packet was sent successfully, False otherwise.
    Warning:
        - The target host must have Wake-on-LAN enabled in its BIOS/UEFI settings.
        - The target host must be connected to the network via a wired connection.
        - WoL packets may not traverse routers unless specifically configured.
    """
    broadcast = '255.255.255.255'
    host_parts = hostname.split('.')
    if len(host_parts) == 4:
        if all(0 <= int(x) < 256 for x in host_parts):
            broadcast = '.'.join(host_parts[:3] + ['255'])

    logger.info(f"Sending WoL packet to {mac_address} on broadcast {broadcast}")  # type: ignore
    try:
        mac_address = mac_address.replace(":", "").replace("-", "").replace(".", "")
        if len(mac_address) != 12:
            raise ValueError(f"Invalid MAC address: {mac_address}")
        
        mac_bytes = bytes.fromhex(mac_address)
        magic_packet = b"\xFF" * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (broadcast, port))
            return True
    except ValueError as e:
        logger.error(f"Wake-on-LAN failed: {e}")  # type: ignore
        return False
    except Exception as e:
        logger.error(f"Wake-on-LAN failed: {e}")  # type: ignore
        return False