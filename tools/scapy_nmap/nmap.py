import dataclasses
import enum
import random
import sys
import time
import typing

import rich
from rich.progress import Progress
from rich.table import Table
from scapy.all import ICMP, IP, TCP, sr1


@dataclasses.dataclass
class PortAnalysis:
    port: int
    result: str


class Verdicts(enum.Enum):
    OPEN = 'open'
    FILTERED = 'filtered'
    CLOSED = 'closed'


class TCPFlags(enum.Enum):
    SYN_ACK = 0x12
    ACK_RST = 0x14


def _print_result(
    host_address: str, ports: str,
    analysis_result: typing.List[PortAnalysis],
) -> None:
    table = Table(
        title=(
            f'\nPorts scan results'
            f'\nHost: {host_address} '
            f'\nAnalyzed port range: {ports}'
        ),
        title_justify='left',
        title_style='bold magenta',
        width=50,
    )
    table.add_column("Ports", no_wrap=False, justify="left", style="green")
    table.add_column("Results", no_wrap=False, justify="left", style="green")
    for analyzed_ports in analysis_result:
        table.add_row(str(analyzed_ports.port), str(analyzed_ports.result))
    rich.print(table)


def _get_ports_analysis(
    host_address: str, ports: str,
) -> typing.List[PortAnalysis]:
    ports_analysis_map: typing.List[PortAnalysis] = []
    port_start, port_end = map(int, ports.split('-'))
    ports_range = [port for port in range(port_start, port_end + 1)]
    rich.print(f'[+] Ports scanning:\n{"-" * 21}')
    with Progress() as progress:
        task = progress.add_task("[green]Scaning...", total=len(ports_range))
        for dst_port in ports_range:
            # Send SYN with random Src Port for each Dst port
            src_port = random.randint(1025, 65534)
            request_syn = IP(dst=host_address) / TCP(
                sport=src_port, dport=dst_port, flags="S"
            )
            answer = sr1(request_syn, timeout=2, retry=1, verbose=False)
            if answer is None:
                ports_analysis_map.append(
                    PortAnalysis(dst_port, Verdicts.FILTERED.value)
                )
            elif TCP in answer:

                if answer[TCP].flags == TCPFlags.SYN_ACK.value:
                    ports_analysis_map.append(
                        PortAnalysis(dst_port, Verdicts.OPEN.value)
                    )
                elif answer[TCP].flags == TCPFlags.ACK_RST.value:
                    ports_analysis_map.append(
                        PortAnalysis(dst_port, Verdicts.CLOSED.value)
                    )
            # https://www.ibm.com/docs/en/qsip/7.4?topic=applications-icmp-type-code-ids
            elif (
                ICMP in answer and int(answer[ICMP].type) == 3
                and int(answer[ICMP].code) in [1, 2, 3, 9, 10, 13]
            ):
                ports_analysis_map.append(
                    PortAnalysis(dst_port, Verdicts.FILTERED.value)
                )
            progress.update(task, advance=1)
    return ports_analysis_map


def main() -> None:
    start_time = time.monotonic()
    if len(sys.argv) != 3:
        rich.print(
            "[red]Invalid input params![/red]\n"
            "Correct example: nmap.py 10.0.0.1/24 80-120"
        )
        exit(1)
    analysis_result: typing.List[PortAnalysis] = _get_ports_analysis(
        host_address=sys.argv[1], ports=sys.argv[2],
    )
    _print_result(
        host_address=sys.argv[1], ports=sys.argv[2],
        analysis_result=analysis_result
    )
    end_time = time.monotonic()
    rich.print(f'[+] Scan time: {end_time - start_time} s.')


if __name__ == '__main__':
    main()
