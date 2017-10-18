#!/bin/bash



sudo sh -c "echo '340' > /sys/class/gpio/export"
sudo sh -c "echo 'out' > /sys/class/gpio/gpio340/direction"
sudo sh -c "echo '0' > /sys/class/gpio/gpio340/value"

sudo sh -c "echo '339' > /sys/class/gpio/export"
sudo sh -c "echo 'out' > /sys/class/gpio/gpio339/direction"
sudo sh -c "echo '0'> /sys/class/gpio/gpio339/value"

sudo sh -c "echo '338' > /sys/class/gpio/export"
sudo sh -c "echo 'out' > /sys/class/gpio/gpio338/direction"
sudo sh -c "echo '0' > /sys/class/gpio/gpio338/value"

sudo sh -c "echo '475' > /sys/class/gpio/export"
sudo sh -c "echo 'out' > /sys/class/gpio/gpio475/direction"
sudo sh -c "echo '0' > /sys/class/gpio/gpio475/value"


