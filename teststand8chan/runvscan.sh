#!/bin/bash

python voltagescan.py 5.0 --vmin=63.8 --vmax=72.1 --deltav=0.2 --trim=0.5
python voltagescan.py 5.0 --vmin=64.8 --vmax=72.1 --deltav=0.2 --trim=1.5
python voltagescan.py 5.0 --vmin=65.8 --vmax=72.1 --deltav=0.2 --trim=2.5
python voltagescan.py 5.0 --vmin=66.8 --vmax=72.1 --deltav=0.2 --trim=3.5
python voltagescan.py 5.0 --vmin=67.8 --vmax=72.1 --deltav=0.2 --trim=4.5
