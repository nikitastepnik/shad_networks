# Отчет о выполнении лабораторной работы scapy_mtr
**Программа на 50 баллов**  
Разработана утилита аналог команды ping.  
Пример запуска: `python3 ping.py ya.ru`
В случае неправильной конфигурации входных данных, пользователь будет уведомлен об этом:
![alt text](invalid_input.png)

## Тестирование
Попробуем попинговать хост `ya.ru` с помощью созданного скрипта и оригинальной утилиты:  
```
nikitaadmin@nistepanovvirtual:~/nistepanov/tools/scapy_mtr$ sudo python3 ping.py ya.ru
PING ya.ru (5.255.255.242): 18 data bytes
18 bytes from 5.255.255.242: icmp_seq=1 ttl=56 time=17.162 ms
18 bytes from 5.255.255.242: icmp_seq=2 ttl=56 time=17.162 ms
18 bytes from 5.255.255.242: icmp_seq=3 ttl=56 time=17.162 ms
18 bytes from 5.255.255.242: icmp_seq=4 ttl=56 time=17.162 ms
18 bytes from 5.255.255.242: icmp_seq=5 ttl=56 time=17.162 ms
18 bytes from 5.255.255.242: icmp_seq=6 ttl=56 time=17.162 ms
^C
--- ya.ru ping statistics ---
7 packets transmitted, 7 packets received, 0.0% packet loss
```
```
nikitaadmin@nistepanovvirtual:~/nistepanov/tools/scapy_mtr$ ping ya.ru
PING ya.ru (77.88.55.242) 56(84) bytes of data.
64 bytes from ya.ru (77.88.55.242): icmp_seq=1 ttl=56 time=6.20 ms
64 bytes from ya.ru (77.88.55.242): icmp_seq=2 ttl=56 time=6.04 ms
64 bytes from ya.ru (77.88.55.242): icmp_seq=3 ttl=56 time=6.02 ms
64 bytes from ya.ru (77.88.55.242): icmp_seq=4 ttl=56 time=6.03 ms
64 bytes from ya.ru (77.88.55.242): icmp_seq=5 ttl=56 time=6.11 ms
64 bytes from ya.ru (77.88.55.242): icmp_seq=6 ttl=56 time=6.03 ms
^C
--- ya.ru ping statistics ---
6 packets transmitted, 6 received, 0% packet loss, time 5007ms
rtt min/avg/max/mdev = 6.015/6.071/6.203/0.066 ms
```

Теперь попингуем невалидный хост `nikita.ru`:
```  
nikitaadmin@nistepanovvirtual:~/nistepanov/tools/scapy_mtr$ sudo python3 ping.py ya.ru
PING ya.ru (77.88.55.242): 18 data bytes
18 bytes from 77.88.55.242: icmp_seq=1 ttl=56 time=17.162 ms
18 bytes from 77.88.55.242: icmp_seq=2 ttl=56 time=17.162 ms
18 bytes from 77.88.55.242: icmp_seq=3 ttl=56 time=17.162 ms
18 bytes from 77.88.55.242: icmp_seq=4 ttl=56 time=17.162 ms
^C
--- ya.ru ping statistics ---
5 packets transmitted, 5 packets received, 0.0% packet loss
```

```
nikitaadmin@nistepanovvirtual:~/nistepanov/tools/scapy_mtr$ ping nikita.ru
PING nikita.ru (93.95.102.247): 56 data bytes
Request timeout for icmp_seq 0
Request timeout for icmp_seq 1
Request timeout for icmp_seq 2
Request timeout for icmp_seq 3
Request timeout for icmp_seq 4
Request timeout for icmp_seq 5
Request timeout for icmp_seq 6
Request timeout for icmp_seq 7
^C
--- nikita.ru ping statistics ---
9 packets transmitted, 0 packets received, 100.0% packet loss
```

Видно, что утилиты предоставляют одинаковый результат
