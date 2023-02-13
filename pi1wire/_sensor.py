from ._constant import Resolution
from ._driver import W1DriverInterface
from ._exception import InvalidCRCException
from ._parser import parse_response


class OneWireInterface:

    _mac_address: str

    @property
    def mac_address(self) -> str:
        return self._mac_address

    def get_temperature(self) -> float:
        raise NotImplementedError

    def change_resolution(self, resolution: Resolution, use_sudo: bool = True):
        raise NotImplementedError


class OneWire(OneWireInterface):

    def __init__(self, mac_address: str, driver: W1DriverInterface):
        self._mac_address = mac_address
        self._driver = driver
        self._power_on_reset_values = [85000, 25000]
        self._second_try = False

    def get_temperature(self) -> float:
        r = self._driver.read_w1_data(self._mac_address)
        crc, check, raw_value = parse_response(r)
        if check != 'YES':
            self._second_try = False  # reset
            raise InvalidCRCException(f'Invalid CRC [{crc}]')
        value = int(raw_value)
        if value in self._power_on_reset_values and not self._second_try:
            # Just to be sure: try a re-read because we read a PowerOnResetValue
            self._second_try = True  # Prevent from endless loop
            return self.get_temperature()
        self._second_try = False
        return value / 1000.0

    def change_resolution(self, resolution: Resolution, use_sudo: bool = True):
        self._driver.change_w1_resolution(
            self._mac_address, resolution, use_sudo)
