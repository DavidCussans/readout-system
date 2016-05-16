EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:sipm_socket
LIBS:singlepcb-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L SiPM_Socket U1
U 1 1 5734B77D
P 5450 3350
F 0 "U1" H 5450 3350 60  0000 C CNN
F 1 "SiPM_Socket" H 5450 3350 60  0000 C CNN
F 2 "sipm_socket:sipm_socket" H 5450 3350 60  0001 C CNN
F 3 "" H 5450 3350 60  0000 C CNN
	1    5450 3350
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR01
U 1 1 5734B7B2
P 4700 3200
F 0 "#PWR01" H 4700 2950 50  0001 C CNN
F 1 "GND" H 4700 3050 50  0000 C CNN
F 2 "" H 4700 3200 50  0000 C CNN
F 3 "" H 4700 3200 50  0000 C CNN
	1    4700 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	4700 3200 5000 3200
Wire Wire Line
	5000 3200 5000 3100
Wire Wire Line
	5000 3600 5000 3750
Wire Wire Line
	5000 3750 6250 3750
Wire Wire Line
	6250 3750 6250 3200
Wire Wire Line
	6250 3200 6050 3200
Wire Wire Line
	5000 3500 4900 3500
Wire Wire Line
	4900 3500 4900 3800
Wire Wire Line
	4900 3800 6150 3800
Wire Wire Line
	6150 3800 6150 3500
Wire Wire Line
	6150 3500 6050 3500
$EndSCHEMATC
