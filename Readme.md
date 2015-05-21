SoLid readout system
====================

_Development of the readout system for the full scale SoLid experiment._

The repository is split into the separate development parts:

* sensors - The light sensors and the PCBs
* analog board - to provide bias voltage, amplify and shape the analog signals form the sensors
* digital board - to digitise the analog signals, analyse the signals in an FPGA to make trigger decisions and transmit them to a PC
* software - to collect data transmitted from the FPGA, further reduce the data and write it to disk. The interface for operators to control the system
* cabling - to connect the senors to the analog board, the analog board to the digital board, power supplies to each board, etc.
* docs - system level documents such as requirements, reports, etc.


Permissions
-----------

The `Readout developers` group have write access, other members of the collaboration have read access.
If you need access contact Nick Ryder.
