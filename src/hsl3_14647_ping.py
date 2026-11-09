import subprocess
import platform
import socket
import os
import struct
import time

def ping(host: str, timeout: int = 4) -> bool:
    """
    Execute a simple ping to check if a host is reachable.
    
    Args:
        host: The hostname or IP address to ping
        timeout: Timeout in seconds (default: 4)
    
    Returns:
        True if ping was successful, False otherwise
    Warning:
        - This function uses the system's ping command, which may require appropriate permissions and may not be available in all environments.
        - A ping result is not a definitive indicator of host health, as some hosts may block ping requests, network conditions may affect results, and a successful ping does not guarantee that the host is fully operational.
    """
    try:
        # Determine the ping command based on OS
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "-W", str(timeout * 1000), host]
        
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 2
        )
        print ( f"Ping command output: {result.stdout.decode().strip()}" )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print (f"Ping to {host} timed out.")
        return False
    except Exception as e:
        print(f"Ping failed: {e}")
        return False


def tcp_health_check(host: str, port: int, timeout: int = 4) -> bool:
    """
    Execute a TCP health check to verify if a host is reachable on a specific port.
    
    Args:
        host: The hostname or IP address to check
        port: The port number to connect to
        timeout: Timeout in seconds (default: 4)
    
    Returns:
        True if TCP connection was successful, False otherwise
    """
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            print ( f"TCP health check to {host}:{port} returned code: {result}" )
            return result == 0
    except socket.gaierror:
        print(f"TCP health check failed: hostname {host} could not be resolved")
        return False
    except Exception as e:
        print(f"TCP health check to {host}:{port} failed: {e}")
        return False
    


def icmp_echo_request(host: str, timeout: float = 1.0, payload_size: int = 32) -> bool:
    """
    Send a single ICMP Echo Request and wait for a matching Echo Reply.

    Returns:
        True if a reply is received within timeout, False otherwise.

    """

    def _icmp_checksum(data: bytes) -> int:
        if len(data) % 2:
            data += b"\x00"

        total = 0
        for i in range(0, len(data), 2):
            total += (data[i] << 8) + data[i + 1]
            total = (total & 0xFFFF) + (total >> 16)

        return (~total) & 0xFFFF

    try:
        target_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print(f"ICMP failed: hostname {host} could not be resolved")
        return False

    icmp_type = 8  # Echo Request
    icmp_code = 0
    identifier = os.getpid() & 0xFFFF
    sequence = int(time.time() * 1000) & 0xFFFF
    payload = b"X" * max(1, payload_size)

    header = struct.pack("!BBHHH", icmp_type, icmp_code, 0, identifier, sequence)
    checksum = _icmp_checksum(header + payload)
    packet = struct.pack("!BBHHH", icmp_type, icmp_code, checksum, identifier, sequence) + payload

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as sock:
            sock.settimeout(timeout)
            sent_at = time.time()
            sock.sendto(packet, (target_ip, 0))

            while True:
                if time.time() - sent_at > timeout:
                    print(f"ICMP to {host} timed out.")
                    return False

                data, addr = sock.recvfrom(65535)
                if addr[0] != target_ip:
                    continue

                ip_header_len = (data[0] & 0x0F) * 4
                icmp_header = data[ip_header_len:ip_header_len + 8]
                if len(icmp_header) < 8:
                    continue

                r_type, r_code, _, r_id, r_seq = struct.unpack("!BBHHH", icmp_header)
                if r_type == 0 and r_code == 0 and r_id == identifier and r_seq == sequence:
                    print(f"ICMP echo reply received from {host}")
                    return True

    except PermissionError:
        print("ICMP failed: raw sockets require elevated privileges")
        return False
    except socket.timeout:
        print(f"ICMP to {host} timed out.")
        return False
    except Exception as e:
        print(f"ICMP failed: {e}")
        return False


def wake_on_lan(mac_address: str, broadcast: str = "255.255.255.255", port: int = 9) -> bool:
    """
    Send a Wake-on-LAN magic packet to a host.

    Args:
        mac_address: The MAC address of the target host (e.g., "AA:BB:CC:DD:EE:FF")
        broadcast: The broadcast address to send the packet to (default: "255.255.255.255")
        port: The UDP port to send the packet to (default: 9)

    Returns:
        True if the magic packet was sent successfully, False otherwise.
    
    Warning:
        - The target host must have Wake-on-LAN enabled in its BIOS/UEFI settings.
        - The target host must be connected to the network via a wired connection.
        - WoL packets may not traverse routers unless specifically configured.
    """
    try:
        mac_address = mac_address.replace(":", "").replace("-", "").replace(".", "")
        if len(mac_address) != 12:
            raise ValueError(f"Invalid MAC address: {mac_address}")
        
        mac_bytes = bytes.fromhex(mac_address)
        magic_packet = b"\xFF" * 6 + mac_bytes * 16

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (broadcast, port))
            print(f"Wake-on-LAN magic packet sent to {mac_address} via {broadcast}:{port}")
            return True
    except ValueError as e:
        print(f"Wake-on-LAN failed: {e}")
        return False
    except Exception as e:
        print(f"Wake-on-LAN failed: {e}")
        return False


# def __main__():
#     hosts = [
#              "192.168.3.162"
#              ]
#     for host in hosts:
        
#         if icmp_echo_request(host, timeout=2, payload_size=64):
#             print(f"{host} is reachable via ICMP echo request.")
            
#         elif tcp_health_check(host, 443, timeout=2):
#                 print(f"{host} is reachable on port 80.")
        
#         elif ping(host):
#             print(f"{host} is reachable.")
        
#         else:
#             print(f"{host} is not reachable.")
#             # wake_on_lan("9C:8C:6E:0A:1C:09")  # Replace with actual MAC address if needed   

#         print("\n")
# if __name__ == "__main__":
#     __main__()