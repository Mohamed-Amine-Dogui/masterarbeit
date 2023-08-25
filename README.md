# Masterarbeit : IoT und AWS Cloud Infrastruktur

Willkommen im GitHub-Repository meiner Masterarbeit zum Thema "IoT und AWS Cloud Infrastruktur". Hier finden Sie den Code und die begleitende Dokumentation zu meinem Projekt. Das Hauptziel dieser Arbeit besteht darin, die Umsetzung von Internet of Things (IoT) Technologien in Verbindung mit AWS Cloud Services eingehend zu untersuchen und durch ein Proof of Concept (PoC) zu demonstrieren.

Das Projekt befasst sich mit der Erfassung von Sensordaten mittels IoT-Geräten, der Verarbeitung und Speicherung dieser Daten in der AWS Cloud sowie der Visualisierung der Ergebnisse. Dabei werden wichtige Konzepte wie "Infrastructure as Code" (IaaC) und Cloud Computing angewendet, um eine effiziente, skalierbare und automatisierte Lösung zu entwickeln. Die gesammelten Messwerte werden in nahezu Echtzeit visualisiert und in Grafana dargestellt, um eine umfassende Überwachung und Analyse zu ermöglichen.

Dieses Projekt ist als Proof of Concept (PoC) konzipiert, um die Machbarkeit und Praktikabilität der Integration von IoT-Technologien in die AWS Cloud zu verdeutlichen. Die bereitgestellten Code-Beispiele, Konfigurationen und Dokumentationen dienen als Ressourcen, um den Prozess der Umsetzung zu verstehen und nachvollziehen zu können.

## Inhaltsverzeichnis

- [Hintergrund](#hintergrund)
- [Verwendung](#verwendung)
- [Verzeichnisstruktur](#verzeichnisstruktur)
- [Verwendung des Raspberry Pi 4B](#verwendung-des-raspberry-pi-4b)
- [Skripte und Dateien](#skripte-und-dateien)
- [Workflow und CI/CD](#workflow-und-ci/cd)

## Hintergrund

In dieser Masterarbeit liegt der Fokus auf der umfassenden Integration von IoT-Sensoren in die AWS Cloud-Infrastruktur. Das Hauptziel besteht darin, Daten von Sensoren mithilfe von IoT-Geräten zu erfassen, diese Daten in der AWS Cloud zu verarbeiten, zu speichern und letztlich durch Visualisierung in Grafana anschaulich darzustellen. Dabei kommen essentielle Konzepte wie "Infrastructure as Code" (IaaC) und Cloud Computing zum Einsatz, um eine Lösung zu entwickeln, die höchste Effizienz, Skalierbarkeit und Automatisierung bietet.

Die gesammelten Messwerte werden in Grafana in nahezu Echtzeit visualisiert, was eine aussagekräftige und intuitive Überwachung und Analyse der Sensorwerte ermöglicht. Dieser Ansatz trägt dazu bei, sowohl die technische Umsetzung als auch die praktische Anwendung der IoT-Integration in die Cloud-Infrastruktur zu erforschen und zu demonstrieren.

## Verwendung

Dieses Repository enthält den Quellcode sowie die Konfigurationsdateien für die Implementierung der AWS Cloud-Infrastruktur und die Integration von IoT-Sensoren. Die bereitgestellten Skripte ermöglichen das Auslesen und Übertragen von Temperaturdaten von DS18B20-Temperatursensoren in die AWS Timestream-Datenbank. Zudem wird die Nutzung von Amazon SNS für Alarmbenachrichtigungen demonstriert.

## Verzeichnisstruktur

- `skripts/`: Enthält die Skripte, um Temperaturdaten von DS18B20-Sensoren auszulesen und in die AWS Cloud zu übertragen.
  - `unload_csv.py`: Skript zum Entladen von Daten aus AWS Timestream in CSV-Format.
  - `main.py`: Hauptskript zur Erfassung von Temperaturdaten von DS18B20-Sensoren und Übertragung in AWS Timestream.

Selbstverständlich! Hier ist die aktualisierte Anleitung zur Konfiguration des Raspberry Pi 4B für den DS18B20-Temperatursensor, wobei die Schritte zusammengefasst werden:

## Verwendung des Raspberry Pi 4B

Die Implementierung nutzt einen Raspberry Pi 4B als IoT-Gerät. Hier ist eine kurze Anleitung zur Konfiguration des Raspberry Pi für die Nutzung des DS18B20-Temperatursensors:

1. **Konfigurationsdatei bearbeiten:** Die Konfigurationsdatei "config.txt" im Verzeichnis "/boot" wird geöffnet, um GPIO-Einstellungen des Raspberry Pi anzupassen. Verwenden Sie den Texteditor "nano":
   
   ```bash
   sudo nano /boot/config.txt
   ```

2. **GPIO für DS18B20-Sensor angeben:** Fügen Sie in der "config.txt" folgenden Inhalt hinzu, um den GPIO-Anschluss für den DS18B20-Sensor festzulegen:
   
   ```plaintext
   dtoverlay=w1-gpio,gpiopin=21
   ```

3. **Neustart durchführen:** Führen Sie einen Neustart des Systems durch, damit die vorgenommenen Änderungen wirksam werden:
   
   ```bash
   sudo reboot
   ```

4. **Kernel-Module aktivieren:** Aktivieren Sie die erforderlichen Kernel-Module für die 1-Wire-Schnittstelle und die Temperaturmessung:
   
   ```bash
   sudo modprobe w1-gpio pullup=1
   sudo modprobe w1-therm
   ```

5. **Pfad ändern:** Wechseln Sie zum Verzeichnis, in dem die erfassten Temperaturdaten des DS18B20-Sensors zugänglich gemacht werden:
   
   ```bash
   cd /sys/bus/w1/devices/
   ```

Mit diesen Schritten wird der Raspberry Pi 4B für die Verwendung des DS18B20-Temperatursensors konfiguriert, und Sie können die Temperaturdaten effektiv auslesen und übertragen.

## Ausführen des Cron-Jobs: Erstellung eines täglichen CSV-Berichts

In diesem Abschnitt wird erläutert, wie der Cron-Job eingerichtet wird, um das Python-Skript "unload_csv.py" auf dem Raspberry Pi auszuführen. Dieses Skript ermöglicht die Erstellung eines täglichen CSV-Berichts, der sämtliche Daten vom vorherigen Tag bis zur aktuellen Zeit aus der Timestream-Datenbank enthält.

Um den Cron-Job einzurichten, folgen Sie bitte den nachstehenden Schritten:

1. Fügen Sie am Anfang des Skripts "#!/usr/bin/env python3" ein, um den Python-Interpreter festzulegen.

2. Ermitteln Sie das aktuelle Datum und setzen Sie die Systemzeitzone auf "Europe/Berlin".

```shell
sudo timedatectl set-timezone Europe/Berlin
```

3. Verwenden Sie den Befehl "crontab -e", um den Cron-Job zu bearbeiten. Und fügen Sie die folgende Zeile hinzu, um den Cron-Job einzurichten, der das Skript täglich um 08:00 Uhr ausführt und das Protokoll in "cron_log.txt" speichert:

```shell
00 08 * * * /usr/bin/python3 /home/app/code/unload_csv.py >> /home/app/code/cron_log.txt 2>&1 
```

Durch das Ausführen dieses Skripts wird ein täglicher CSV-Bericht generiert, der sämtliche Daten vom vorherigen Tag bis zur aktuellen Zeit aus der Timestream-Datenbank abruft und in eine CSV-Datei speichert. Dieser Bericht dient zur weiteren Analyse und Auswertung der gesammelten Messdaten.

## Workflow und CI/CD

Die Implementierung der AWS Cloud-Infrastruktur und die Ausführung der Skripte werden mithilfe von GitHub Actions und Terraform automatisiert. Der Workflow in diesem Repository (siehe `.github/workflows/main.yaml`) führt Terraform-Schritte aus, um die Infrastruktur zu erstellen, und verwendet die bereitgestellten Skripte, um Temperaturdaten zu erfassen und in die Cloud zu übertragen.
