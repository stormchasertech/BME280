# Installer for BME280 weewx service

from weecfg.extension import ExtensionInstaller

def loader():
    return BME280_Installer()

class BME280_Installer(ExtensionInstaller):
    def __init__(self):
        super(BME280_Installer, self).__init__(
            version='0.1',
            name='BME280',
            description='Collect data from BME280 sensor',
            author='StormchaserTech',
            data_services='user.BME280.BME280',
            config={
                'BME280': {
                    'i2c_port': '1',
                    'i2c_address': '0x76',
                    'tempKey': 'inTemp',
                    'humidKey': 'inHumidity',
                    'pressureKey': 'pressure'
                }
            },
            files=[('bin/user', ['bin/user/BME280.py'])]
        )
