package main

import (
	"bitbucket.org/solidexperiment/readout-software/frontend"
	"bitbucket.org/NickRyder/goipbus/ipbus"
	"flag"
	"fmt"
	"log"
	"net"
	"strconv"
	"time"
	"os"
)

func main() {
	log.SetFlags(log.LstdFlags | log.Lshortfile)
	setalarm := flag.Float64("alarmtemp", 65.0, "Alarm temperature")
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "%s <last byte of IP address>\n", os.Args[0])
		flag.PrintDefaults()
		fmt.Fprintln(os.Stderr, "see X for instructions.")
	}
	flag.Parse()
	if len(flag.Args()) != 1 {
		log.Fatal("Require one arg as board name IP")
	}
	u, err := strconv.ParseUint(flag.Args()[0], 0, 8)
	if err != nil {
		panic(err)
	}
	addr := fmt.Sprintf("192.168.235.%d:50001", u)
	conn, err := net.Dial("udp", addr)
	if err != nil {
		panic(err)
	}
	t, err := ipbus.New("dut", "addr_tablev12/top.xml", conn)
	if err != nil {
		log.Fatal(err)
	}
	fe, err := frontend.New64ch(&t, "dut", 8)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Using board ID = 0x%012x\n", fe.ID)
	version, err := fe.FirmwareVersion()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Firmware version %04x\n", version)
	digitali2c := fe.I2CBuses[1]
	digitaladdr := uint8(0x18)
	analogi2cs := fe.I2CBuses[:0]
	analogaddr := uint8(0x48)
	fmt.Printf("Configuring temperature monitor...\n")
	indeti2c := fe.I2CBuses[:0]
	indetaddrs := []uint8{}
	tempmon, err := frontend.NewTempMonitor(float32(*setalarm), digitali2c, digitaladdr, analogi2cs, analogaddr, indeti2c, indetaddrs)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("Reading temperatures...\n")
	temps, err := tempmon.Temperatures()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("current temperatures: %+v\n", temps)
	fmt.Printf("Checking current status...\n")
	alarm, err := tempmon.DigitalBoard.Status()
	if err != nil {
		log.Fatal(err)
	}
	if alarm {
		fmt.Printf("Critical temperature alarm!\n")
	} else {
		fmt.Printf("No alarm.\n")
	}
	time.Sleep(5 * time.Second)
	alarm, err = tempmon.DigitalBoard.Status()
	if err != nil {
		log.Fatal(err)
	}
	if alarm {
		fmt.Printf("Critical temperature alarm!\n")
	} else {
		fmt.Printf("No alarm.\n")
	}
}
