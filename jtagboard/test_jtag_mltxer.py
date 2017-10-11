#!/usr/bin/python
import os,sys,argparse

# KEEP THIS AS BELOW! DEPENDS ON AVAILABLE
# GPIO CHANNELS ON MINNOW BOARD
BASE_LOC = "/sys/class/gpio/" 
MINNOW_GPIO_NUMBERS   = [340,339,338,475]

def main():
    channel = -1
    parser  = argparse.ArgumentParser(description=\
                                      'Test JTAG muliplexer channel')
    parser.add_argument('channel', metavar='<channel>', type=int,
                        help='channel to turn on (0...9)')
    parser.add_argument('--execute',action="store_true",
                        help='run with --execute to actually run')
    args    = parser.parse_args()
    channel = args.channel
    execute = args.execute
    if channel < 0 or channel > 9:
        sys.exit("ERROR: Please enter a channel between 0 and 9")
    print("------------------------------------------------------")
    print("Will turn on channel %i of the JTAG multiplexer"%channel)
    print("------------------------------------------------------")

    # below assumes channels have been correctly assigned and
    # made available on the minnow board. This is done through
    # .bash_profile. However check that this is the case before
    # proceeding
    print("INFO: Checking minnow board gpio pins are exported...")
    for c in MINNOW_GPIO_NUMBERS:
        if not os.path.isdir(BASE_LOC+"gpio%d"%c):
            sys.exit("ERROR: Please ensure gpio pins have been "\
                     "exported. You can do this by running the script "\
                     "~/setup_gpio.sh ")
    print("Done!")
    
    # initialise minnow gpio output to zero
    ch_st_dict  = {}
    for c in MINNOW_GPIO_NUMBERS:
        ch_st_dict[c] = 0

    # now interpret channel number into binary
    # and fill corresponding gpio dictionary
    print("INFO: Interpreting channel number to turn on "\
          "appropriate gpio pins...")
    chanbin = '{0:04b}'.format(channel)
    for i,c in enumerate(MINNOW_GPIO_NUMBERS):
        ch_st_dict[c] = chanbin[i:i+1]
        print("\t [gpio:status] = [%d,%s]"%(c,ch_st_dict[c]))
    
    print("INFO: Setting pins to power channel %d "%(channel))
    print("...Needs super-user access...")
    for c in MINNOW_GPIO_NUMBERS:
        # cmd to set all pins to zero first for safety
        cmd_zero = 'sudo sh -c "echo 0 > %sgpio%d/value"'%(BASE_LOC,c)
        # actual cmd
        cmd = 'sudo sh -c "echo %s > %sgpio%d/value"'%(ch_st_dict[c],
                                                       BASE_LOC,c)
        if execute is False:
            print("Dry run cmd: %s"%cmd)
        else:
            os.system(cmd_zero)
            print("Running cmd: %s"%cmd)
            os.system(cmd)
    print("Done!")
        
if __name__ == "__main__":
    main()
