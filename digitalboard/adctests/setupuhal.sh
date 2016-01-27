#!/bin/bash

export LD_LIBRARY_PATH=/opt/cactus/lib:$LD_LIBRARY_PATH
export PATH=/opt/cactus/bin:$PATH
if [ -f /usr/local/bin/thisroot.sh ]; then
    source /usr/local/bin/thisroot.sh
fi
if [ -f /opt/root_v5.34.23/bin/thisroot.sh ]; then
    source /opt/root_v5.34.23/bin/thisroot.sh
fi
if [ -f /software/root/v5.32.00/bin/thisroot.sh ]; then
    source /software/root/v5.32.00/bin/thisroot.sh
fi
export LD_LIBRARY_PATH=$ROOTSYS/lib:$PYTHONDIR/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$ROOTSYS/lib:$PYTHONPATH
