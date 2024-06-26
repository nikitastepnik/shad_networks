# Отчет к лабораторной работе 1: Статическая маршрутизация

## Задание к лабораторной работе:

### 1.0 Разобраться с CLI (Command Line Interface) FRR следуя примеру в Приложении для РС1 и R1.
Разобрался с CLI FRR 
### 1.1 Настроить IP-адресацию на всех устройствах (контейнерах) согласно прилагаемой схеме.
Настроил IP-адресацию на всех устройствах (контейнерах) согласно прилагаемой схеме
### 1.2 Настроить статические маршруты на каждом маршрутизаторе (FRR), согласно заданию
Настроил статическую маршрутизацию согласно заданию.  
Когда происходит разрыв связи между `R1` и `R2`, то также теряется связность между `PC1` и `PC2`. 
Так происходит потому что используемый для маршрута: `PC1 -> R1 -> R2 -> PC2` интерфейс `eth1` выключен.
Можно убедиться, что используется именно `eth1`:
1) Запустим команду `traceroute 192.168.22.4 (PC2)`, будучи на `PC1`, при этом связь не разорвана:  
```
PC1# traceroute 192.168.22.4
traceroute to 192.168.22.4 (192.168.22.4), 30 hops max, 46 byte packets
 1  192.168.11.1 (192.168.11.1)  0.006 ms  0.004 ms  0.002 ms
 2  192.168.1.2 (192.168.1.2)  0.002 ms  0.005 ms  0.004 ms
 3  192.168.22.4 (192.168.22.4)  0.002 ms  0.004 ms  0.002 ms
```
Видно, что второй узел маршрута это `192.168.1.2`  
2) С другой стороны, посмотрим на маршрутизацию самого `R1`  
```
router1# sh run
ip route 192.168.22.0/24 192.168.1.2 eth1
ip route 192.168.33.0/24 192.168.2.3 eth2
ip route 10.10.10.2/32 192.168.1.2 eth1
ip route 10.10.10.3/32 192.168.2.3 eth2
```
Обратим внимание на `ip route 192.168.22.0/24 192.168.1.2 eth1`, видно что для сязью с подсетью `192.168.22.0/24` используется шлюз `192.168.1.2` и интерфейс `eth1`  
Именно этот интерфейс роутера `R1` был отключен, соотвественно связь между `PC1 -> PC2` обрывается  
3) Убедимся, что маршрут действительно обрывается на узле, предшествующему `192.168.1.2`:  
Выполняем команду `traceroute 192.168.22.4 (PC2)`, будучи на `PC1`, при этом связь разорвана:
```  
PC1# traceroute 192.168.22.4
traceroute to 192.168.22.4 (192.168.22.4), 30 hops max, 46 byte packets
 1  192.168.11.1 (192.168.11.1)  0.005 ms  0.005 ms  0.004 ms
 2^ZPC1# 
PC1#   *  *  *
 3  *  *  *
```
Убеждаемся, что при разорванной связи пакет не доходит.
### 1.3 Написать генератор конфигурации для остальных PC и R маршрутизаторов на Python
Генератор конфигурации реализован в файле: `src/tsk1.3/conf_generator.py`  
**Предварительные требования**:  
Необходимо, чтобы были произведены базовые настройки окружения. То есть все контейнеры топологии должны быть подняты и активны.  
**Инструкция**:  
Скрипт сам подключается к необходимым узлам топологии (контейнерам) и выполняет необходимые команды.   
При этом все исполняыемые команды записываются в соответствующие `.conf` файлы.  
Для каждого устройства – свой файл. В качестве примеры файлы так же приложены, находятся по пути:
`src/tsk1.3/artifacts/**`
### 1.4 Написать скрипт на Python, делающий парсинг вывода
Генератор конфигурации реализован в файле: `src/tsk1.4/parse_node_commands.py`.  
В файл `output.txt` записываются все исполняемые команды, а так же их результат.  
Пример файла находится по пути: `src/tsk1.4/artifacts/output.txt`
