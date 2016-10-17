import argparse

import frontend

parser = argparse.ArgumentParser()
parser.add_argument("-B", "--Board", default="SoLidFPGA")
args = parser.parse_args()

fpga = frontend.SoLidFPGA(args.Board, 1)
