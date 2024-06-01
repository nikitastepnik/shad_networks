import enum
import signal
import sys
import time

import rich
from scapy.all import ICMP, IP, sr1

STOP_PING = False


class ICMPTypes(enum.Enum):
    ECHO_REPLY = 0


def _signal_handler(signum, frame, ) -> None:
    global STOP_PING
    STOP_PING = True


def _ping(host: str, ) -> None:
    icmp = IP(dst=host)/ICMP()
    is_first_ping = True
    iters, successful_pings = 0, 0
    while not STOP_PING:
        reply = sr1(icmp, timeout=1, verbose=False)
        if reply and IP in reply:
            if is_first_ping and reply[ICMP].type == ICMPTypes.ECHO_REPLY.value:
                print(
                    f"PING {host} ({reply[IP].src}): {len(reply[IP].payload)} data bytes")
                is_first_ping = False
                successful_pings += 1
            elif reply[ICMP].type == ICMPTypes.ECHO_REPLY.value:
                time_formatted = "{:.3f}".format(reply[ICMP].time / 10 ** 8)
                print(
                    f"{len(reply[IP].payload)} bytes from {reply[IP].src}: icmp_seq={iters} "
                    f"ttl={reply[IP].ttl} "
                    f"time={time_formatted} ms"
                )
                successful_pings += 1
            else:
                print(f"Request timeout for icmp_seq {iters}")
                break
        else:
            print(f"Request timeout for icmp_seq {iters}")
        iters += 1
        time.sleep(1)
    print("\n---", host, "ping statistics ---")
    print(
        f"{iters} packets transmitted, {successful_pings} packets received, "
        f"{((iters - successful_pings) / iters) * 100:.1f}% packet loss"
    )


if __name__ == '__main__':
    if len(sys.argv) != 2:
        rich.print(
            "[red]Invalid input params![/red]\n"
            "Correct example: ping ya.ru"
        )
        exit(1)
    signal.signal(signal.SIGINT, _signal_handler)
    _ping(host=sys.argv[1])
