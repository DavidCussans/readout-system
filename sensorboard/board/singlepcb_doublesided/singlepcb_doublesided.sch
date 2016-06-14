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
LIBS:idc4
LIBS:sipm
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
L SiPM U1
U 1 1 575E9D54
P 6650 3700
F 0 "U1" H 7000 3700 60  0000 C CNN
F 1 "SiPM" H 6650 3700 60  0000 C CNN
F 2 "sipm:sipm" H 6650 3700 60  0001 C CNN
F 3 "" H 6650 3700 60  0000 C CNN
	1    6650 3700
	1    0    0    -1  
$EndComp
$Comp
L IDC4 S1
U 1 1 575E9DAD
P 4750 3800
F 0 "S1" H 5000 3800 60  0000 C CNN
F 1 "IDC4" H 4750 3800 60  0000 C CNN
F 2 "idc4:idc4" H 4750 3800 60  0001 C CNN
F 3 "" H 4750 3800 60  0000 C CNN
	1    4750 3800
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR01
U 1 1 575E9E42
P 5600 3200
F 0 "#PWR01" H 5600 2950 50  0001 C CNN
F 1 "GND" H 5600 3050 50  0000 C CNN
F 2 "" H 5600 3200 50  0000 C CNN
F 3 "" H 5600 3200 50  0000 C CNN
	1    5600 3200
	1    0    0    -1  
$EndComp
Wire Wire Line
	5100 3600 5250 3600
Wire Wire Line
	5250 3200 5250 3700
Wire Wire Line
	5250 3200 5600 3200
Wire Wire Line
	5250 3700 5100 3700
Connection ~ 5250 3600
Wire Wire Line
	5100 3900 5800 3900
Wire Wire Line
	5800 3900 5800 3800
Wire Wire Line
	5800 3800 6400 3800
Wire Wire Line
	6400 3600 5600 3600
Wire Wire Line
	5600 3600 5600 4000
Wire Wire Line
	5600 4000 5100 4000
$EndSCHEMATC
