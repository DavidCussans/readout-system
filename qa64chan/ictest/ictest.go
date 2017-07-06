// Program ictest confirms that all ICs and communications buses are working
package main

import (
	"bitbucket.org/NickRyder/goipbus/ipbus"
	"bitbucket.org/solidexperiment/readout-software/frontend"
	"bitbucket.org/solidexperiment/readout-software/frontend/comms"
	"bitbucket.org/solidexperiment/readout-software/frontend/ics"
	"flag"
	"fmt"
	"io/ioutil"
	"net"
	"os"
	"os/user"
	"strconv"
	"strings"
	"time"
)

type Result string

const (
	ResSuccess Result = "success"
	ResFailure Result = "failure"
	ResWarning Result = "warning"
)

type Report struct {
		Now time.Time
		ID frontend.PlaneID
		Address string
		Tester string
		Results map[string]Result

}

func New() Report {
	res := make(map[string]Result)
	u, err := user.Current()
	user := ""
	if err == nil {
		user = u.Username
	}
	return Report{Now: time.Now(), Results:res, Tester: user}
}

var tests []string = []string{
	"Contact",
	"UniqueID",
	"DigitalI2C",
	"PowerChips",
	"Voltages",
	"Currents",
	"LM82Temp",
	"InDetectorI2C",
	"Temperature",
	"ADCControl",
	"Analog0I2C",
	"Analog1I2C",
	"ClockSA"}

func (r Report) Write() error {
	now := r.Now.Format("02Jan06_1504")
	msg := fmt.Sprintf("Time: %s\nTester: %s\n", now, r.Tester)
	msg += fmt.Sprintf("Board: %012x\n", r.ID)
	msg += fmt.Sprintf("Address: %s\nTests:\n", r.Address)
	fail := false
	nwarn := 0
	for _, test := range tests {
		res := r.Results[test]
		msg += fmt.Sprintf("\t%s:\t%s\n", test, string(res))
		if res == ResFailure {
			fail = true
		}
		if res == ResWarning {
			nwarn++
		}
	}
	data := []byte(msg)
	fn := fmt.Sprintf("reports/report_ictest_%012x_%s.txt", r.ID, now)
	fmt.Println(msg)
	fmt.Printf("Writing report to %s\n", fn)
	if nwarn > 0 {
		fmt.Printf("\n\nBoard %012x has %d warnings\n", r.ID, nwarn)
	} else {
		if !fail {
			fmt.Printf("\n\nBoard %012x: PASS\n", r.ID)
		}
	}
	if fail {
		fmt.Printf("\n\nBoard %012x: FAIL\n", r.ID)
	}
	return ioutil.WriteFile(fn, data, 0644)
}

var report Report

func Write() {
	report.Write()
}

func main() {
	// Parse command line to get IP
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "Usage of %s:\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "%s <last byte of IP address>\n", os.Args[0])
		flag.PrintDefaults()
		fmt.Fprintln(os.Stderr, "see X for instructions.")
	}
	notemp := flag.Bool("notemp", false, "Flag that there are no external temperature sensors")
	flag.Parse()
	if len(flag.Args()) != 1 {
		flag.Usage()
		os.Exit(1)
	}
	report = New()
	defer Write()
	// Create target given IP address
	u, err := strconv.ParseUint(flag.Args()[0], 0, 8)
	if err != nil {
		panic(err)
	}
	addr := fmt.Sprintf("192.168.235.%d:50001", u)
	conn, err := net.Dial("udp", addr)
	if err != nil {
		report.Results["Contact"] = ResFailure
		panic(err)
	}
	fmt.Printf("Using device with address = %s\n", addr)
	t, err := ipbus.New("dut", "addr_tablev12/top.xml", conn)
	if err != nil {
		report.Results["Contact"] = ResFailure
		panic(err)
	}

	digi, err := frontend.New64chDigital(&t, "dut")
	if err != nil {
		// Need to check what other errors they could be
		// since creating front end already tries to 
		// use various components
		report.Results["Contact"] = ResFailure
	}
	fw, err := digi.FirmwareVersion()
	if err != nil {
		panic(err)
	}
	if fw != 13 {
		err := fmt.Errorf("Invalid firmware version: %d not 13", fw)
		panic(err)
	}
	report.Results["Contact"] = ResSuccess
	// ID chip, if New64chDigital worked then it is correct
	report.ID = digi.ID
	report.Address = addr
	report.Results["UniqueID"] = ResSuccess
	report.Results["DigitalI2C"] = ResSuccess
	fmt.Printf("Board unique ID = %012x\n", digi.ID)
	// Power
	power, err := digi.Power.ReadPower()
	if err != nil {
		report.Results["PowerChips"] = ResFailure
		panic(err)
	}
	report.Results["PowerChips"] = ResSuccess
	fmt.Printf("%v\n", power)
	// Check voltages
	dv := (power.V5_3v3 - 5.0) / 5.0
	warn := false
	if dv > 0.1 || dv < -0.1 {
		report.Results["Voltages"] = ResFailure
		err := fmt.Errorf("5.0 -> 3.3 V regulator input out of range: %0.2f V, %.02f", power.V5_3v3, dv)
		panic(err)
	} else if dv > 0.1 || dv < -0.1 {
		warn = true
		fmt.Printf("Warning: 5.0 -> 3.3 V regulator input out near edge range: %0.2f V", power.V5_3v3)
	}
	dv = (power.V5_2v5 - 5.0) / 5.0
	if dv > 0.1 || dv < -0.1 {
		report.Results["Voltages"] = ResFailure
		err := fmt.Errorf("5.0 -> 3.3 V regulator input out of range: %0.2f V", power.V5_2v5)
		panic(err)
	} else if dv > 0.1 || dv < -0.1 {
		warn = true
		fmt.Printf("Warning: 5.0 -> 2.5 V regulator input out near edge range: %0.2f V", power.V5_2v5)
	}
	dv = (power.V3v3 - 3.3) / 3.3
	if dv > 0.1 || dv < -0.1 {
		report.Results["Voltages"] = ResFailure
		err := fmt.Errorf("3.3 V regulator out of range: %0.2f V", power.V3v3)
		panic(err)
	} else if dv > 0.1 || dv < -0.1 {
		warn = true
		fmt.Printf("Warning: 3.3 V regulator near edge of range: %0.2f V", power.V3v3)
	}
	dv = (power.V1v8 - 1.8) / 1.8
	if dv > 0.1 || dv < -0.1 {
		report.Results["Voltages"] = ResFailure
		err := fmt.Errorf("1.8 V regulator out of range: %0.2f V", power.V1v8)
		panic(err)
	} else if dv > 0.1 || dv < -0.1 {
		warn = true
		fmt.Printf("Warning: 1.8 V regulator near edge of range: %0.2f V", power.V1v8)
	}
	if warn {
		report.Results["Voltages"] = ResWarning
	} else {
		report.Results["Voltages"] = ResSuccess
	}
	// Check currents
	if power.I3v3 > 1.0 || power.I3v3 < 0.5 {
		report.Results["Currents"] = ResFailure
		err := fmt.Errorf("3.3 V current out of range: %0.2f V", power.I3v3)
		panic(err)
	}
	if power.I2v5 > 0.2 {
		report.Results["Currents"] = ResFailure
		err := fmt.Errorf("2.5 V current out of range: %0.2f V", power.I3v3)
		panic(err)
	}
	if power.I1v8 > 2.5 || power.I1v8 < 1.5 {
		report.Results["Currents"] = ResFailure
		err := fmt.Errorf("1.8 V current out of range: %0.2f V", power.I3v3)
		panic(err)
	}
	report.Results["Currents"] = ResSuccess
	// Check digital board temperature
	alarmtemp := float32(80.0)
	digitali2c := digi.I2CBuses[1]
	digitaladdr := uint8(0x18)
	indeti2c := make([]comms.I2C, 0, 2)
	indeti2c = append(indeti2c, digi.I2CBuses[3])
	indetaddress := []uint8{0x48}
	tempmon, err := frontend.NewTempMonitor(alarmtemp, digitali2c, digitaladdr, []comms.I2C{}, uint8(0), indeti2c, indetaddress)
	if err != nil {
		if strings.Contains(err.Error(), "LM82") {
			report.Results["LM82Temp"] = ResFailure
			panic(err)
		} else if strings.Contains(err.Error(), "AT30") {
			report.Results["LM82Temp"] = ResSuccess
			if !*notemp {
				report.Results["InDetectorI2C"] = ResFailure
			} else {
				report.Results["InDetectorI2C"] = ResWarning
				fmt.Printf("Warning: In detector I2C bus not tested\n")
			}

			tempmon, err = frontend.NewTempMonitor(alarmtemp, digitali2c, digitaladdr, []comms.I2C{}, uint8(0), []comms.I2C{}, []uint8{})
			if err != nil {
				panic(err)
			}
		}
	}
	temps, err := tempmon.Temperatures()
	if err != nil {
		report.Results["LM82Temp"] = ResFailure
		report.Results["InDetectorI2C"] = ResFailure
		panic(err)
	}
	report.Results["LM82Temp"] = ResSuccess
	if _, ok := report.Results["InDetectorI2C"]; !ok {
		report.Results["InDetectorI2C"] = ResSuccess
	}
	digitemp := temps[0]
	fmt.Printf("Digital board temperature %0.0f C\n", digitemp)
	if len(temps) > 1 {
		indettemp := temps[1]
		fmt.Printf("External temperature %0.0f C\n", indettemp)
	}
	if digitemp > 60.0 {
		report.Results["Temperature"] = ResFailure
		panic(fmt.Errorf("Digital board temperature too high: %0.1f", digitemp))
	}
	report.Results["Temperature"] = ResSuccess
	// Check ADCs working
	if err := digi.ConfigureADCs(); err != nil {
		report.Results["ADCControl"] = ResFailure
	}
	report.Results["ADCControl"] = ResSuccess
	// Check comms with analog boards
	i2canalog0 := digi.I2CBuses[2]
	i2canalog1 := digi.I2CBuses[3]
	hvaddr := uint8(0x61)
	hvdac := ics.NewMCP4725(i2canalog0, hvaddr, 4.6)
	if _, err := hvdac.Read(); err != nil {
		report.Results["Analog0I2C"] = ResFailure
	}
	report.Results["Analog0I2C"] = ResSuccess
	hvdac = ics.NewMCP4725(i2canalog1, hvaddr, 4.6)
	if _, err := hvdac.Read(); err != nil {
		report.Results["Analog1I2C"] = ResFailure
	}
	report.Results["Analog1I2C"] = ResSuccess
	// Check clock chip
	if err := digi.Reset("Si5345-RevB-SOL64CSA-Registers.txt"); err != nil {
		report.Results["ClockSA"] = ResFailure
		panic(err)
	}
	report.Results["ClockSA"] = ResSuccess

}
