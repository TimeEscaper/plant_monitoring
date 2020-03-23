"""
Default light driver that is designed
to control light via separate Arduino board
"""
class LightDriver:
    """
    :param hardware_interface_queue a queue that connects driver with interface IO thread.
    """
    def __init__(self, hardware_interface_queue):
        self.queue_ = hardware_interface_queue

    """
    Switches light on.
    :param pin Integer, pin number
    """
    def light_on(self, pin):
        self.queue_.put("on" + str(pin))

    """
    Switches light on.
    :param pin Integer, pin number
    """
    def light_off(self, pin):
        self.queue_.put("off" + str(pin))
