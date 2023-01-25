"""
Weewx Service that reads BME280 observation data and adds it to loop packets

Requires BME280 python driver (RPi.bme280) https://pypi.org/project/RPi.bme280/

"""
import smbus2
import bme280
import logging
import weewx
from weewx.units import ValueTuple
from weewx.engine import StdService

log = logging.getLogger(__name__)

class BME280(StdService):
    
    def __init__(self, engine, config_dict):

        super(BME280, self).__init__(engine, config_dict)
        self.BME280_dict = config_dict.get('BME280', {})
        log.info('BME280 configuration loaded')

        ## Gather information required by BME280 Driver 
        self.port = int(self.BME280_dict.get('i2c_port'))
        self.address = int(self.BME280_dict.get('i2c_address'), base=16)
        self.bus = smbus2.SMBus(self.port)
        self.calibration_params = bme280.load_calibration_params(self.bus, self.address)

        ## Gather weewx data keys from weewx.conf
        self.tempKey = self.BME280_dict.get('tempKey')
        self.humidKey = self.BME280_dict.get('humidKey')
        self.pressureKey = self.BME280_dict.get('pressureKey')

        ## Add BME280 info to loop packet
        self.bind(weewx.NEW_LOOP_PACKET, self.new_packet_loop)

    def new_packet_loop(self, event):
        ## Get current observation from the BME280
        data = bme280.sample(self.bus, self.address, self.calibration_params) 

        ## Apply weewx units/group
        temperature_vt = ValueTuple(data.temperature, 'degree_C', 'group_temperature')
        humidity_vt = ValueTuple(data.humidity, 'percent', 'percent')
        pressure_vt = ValueTuple(data.pressure, 'hPa', 'group_pressure')

        ## Convert units if needed
        if 'usUnits' in event.packet:
            temperature_vt = weewx.units.convert(temperature_vt, 'degree_F')
            pressure_vt = weewx.units.convert(pressure_vt, 'inHg')

        ## Build observation dict
        bme280obs = {
            self.tempKey : temperature_vt[0],
            self.humidKey : humidity_vt[0],
            self.pressureKey : pressure_vt[0]
        }

        ## Add observation to loop packet
        event.packet.update(bme280obs)
