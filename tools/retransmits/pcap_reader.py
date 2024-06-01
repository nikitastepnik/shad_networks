import argparse
import dataclasses
import enum
import typing

import matplotlib.pyplot as plt
from scapy.layers.inet import TCP, IP
from scapy.all import *

MAX_WINDOW_SIZE_BYTES = 2 ** 16


class TCPFlags(enum.Enum):
    FIN = 0x01
    SYN = 0x02


@dataclasses.dataclass
class PacketsSummaryAnalysis:
    retransmits_ids: typing.List[int]
    retransmits_on_timestamp: typing.Dict[int, int]
    utilization_on_timestamp: typing.Dict[int, int]


def _visualise_data(
        title: str, x_values: typing.List[int], y_values: typing.List[int],
        x_title: str, y_title: str, result_file: str,
) -> None:
    plt.figure(figsize=(10, 5))
    plt.grid()
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.style.use('ggplot')
    plt.legend()
    plt.plot(x_values, y_values, label=title)
    plt.savefig(result_file)
    plt.close()


def _get_packet_session_id(ip_layer: IP, tcp_layer: TCP, ) -> typing.Tuple:
    return ip_layer.src, ip_layer.dst, tcp_layer.sport, tcp_layer.dport


def _get_packets_analysis(pcap_file) -> PacketsSummaryAnalysis:
    retransmits_ids: typing.List[int] = []
    retransmits_on_timestamp: typing.Dict[int, int] = collections.defaultdict(int)
    utilization_on_timestamp: typing.Dict[int, int] = collections.defaultdict(int)
    already_seen_seq_nums: typing.Dict[typing.Tuple, set] = collections.defaultdict(set)
    packets = rdpcap(pcap_file)
    for idx, packet in enumerate(packets, 1):
        if not packet.haslayer(TCP):
            continue
        timestamp = int(packet.time)
        utilization_on_timestamp[timestamp] += len(packet)
        ip_layer = packet.getlayer(IP)
        tcp_layer = packet.getlayer(TCP)
        packet_session_id: typing.Tuple = _get_packet_session_id(ip_layer, tcp_layer)
        seq_num = tcp_layer.seq
        seg_len = len(tcp_layer.payload)
        if seg_len > 0 or tcp_layer.flags & TCPFlags.FIN.value or tcp_layer.flags & TCPFlags.SYN.value:
            if seq_num in already_seen_seq_nums[packet_session_id]:
                retransmits_ids.append(idx)
                retransmits_on_timestamp[timestamp] += 1
            else:
                already_seen_seq_nums[packet_session_id].add(seq_num)
    return PacketsSummaryAnalysis(
        retransmits_ids=retransmits_ids,
        retransmits_on_timestamp=retransmits_on_timestamp,
        utilization_on_timestamp=utilization_on_timestamp,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PCAP reader')
    parser.add_argument('-f', '--file', metavar='<pcap file name>',
                        help='pcap file to parse', required=True)
    args = parser.parse_args()
    pcap_file = args.file
    if not os.path.isfile(pcap_file):
        print('"{}" does not exist'.format(pcap_file), file=sys.stderr)
        sys.exit(-1)
    packets_analysis: PacketsSummaryAnalysis = _get_packets_analysis(pcap_file)
    with open(f'retransmits_id_{str(pcap_file).split(".")[0]}.txt', 'w') as output_file:
        for packet_id in packets_analysis.retransmits_ids:
            output_file.write(f"{packet_id}\n")
    _visualise_data(
        title='Number of retransmits depending on time',
        x_values=list(sorted(packets_analysis.retransmits_on_timestamp.keys())),
        y_values=list(packets_analysis.retransmits_on_timestamp.values()),
        x_title='Time (sec)',
        y_title='Number of retransmits',
        result_file=f'retransmits_{str(pcap_file).split(".")[0]}.png'
    )
    _visualise_data(
        title='Bandwidth utilization depending on time',
        x_values=list(sorted(packets_analysis.utilization_on_timestamp.keys())),
        y_values=list(packets_analysis.utilization_on_timestamp.values()),
        x_title='Time (sec)',
        y_title='Bandwidth',
        result_file=f'utilization_{str(pcap_file).split(".")[0]}.png'
    )
