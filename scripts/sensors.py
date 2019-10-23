import smbus
import time
import os
import pandas as pd
import numpy as np
import logging

def readMessageFromArduino(sensors_settings):
    logger = logging.getLogger('root')
    bus = smbus.SMBus(1)
    SLAVE_ADDRESS = 0x04
    smsMessage = ""
    data_received_from_Arduino = bus.read_i2c_block_data(SLAVE_ADDRESS, 0, 32)
    length_sms = len(data_received_from_Arduino)

    for i in range(length_sms):
        smsMessage += chr(data_received_from_Arduino[i])

    pars = smsMessage.split(';')

    return pars
