import smbus


"""
Driver for interacting with Arduino over I2C.
"""
class I2CDriver:
    """
    :param slave_address I2C slave address
    """
    def __init__(self, slave_address):
        self.slave_address_ = slave_address

    """
    Sends message to slave.
    :param message A string with message to send.
    """
    def send_message(self, message):
        bus = smbus.SMBus(1)
        bytes_val = []
        for c in message:
            bytes_val.append(ord(c))
        bus.write_i2c_block_data(self.slave_address_, 0x00, bytes_val)
