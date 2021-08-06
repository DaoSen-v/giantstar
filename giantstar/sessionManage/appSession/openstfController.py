import requests


class OpenstfController:
    host = ""
    headers = {}
    serials = []
    @classmethod
    def devices(cls):
        url = 'http://{}/api/v1/devices'.format(cls.host)
        response = requests.get(url, headers=cls.headers)
        return response.json()

    @classmethod
    def device_info(cls, serial_no):
        """获取指定设备详情"""
        url = 'http://{}/api/v1/devices/{}'.format(cls.host, serial_no)
        response = requests.get(url, headers=cls.headers)
        return response

    @classmethod
    def current_devices(cls):
        url = 'http://{}/api/v1/user/devices'.format(cls.host)
        response = requests.get(url, headers=cls.headers)
        return response

    @classmethod
    def acquire_debug_address(cls, serial_no):
        url = 'http://{}/api/v1/user/devices/{}/remoteConnect'.format(cls, serial_no)
        response = requests.post(url, headers=cls.headers)
        return response

    @classmethod
    def release_device(cls):
        for serial in cls.serials:
            url = 'http://{}/api/v1/user/devices/{}'.format(cls.host, serial)
            body = {'serial': serial}
            requests.post(url, headers=cls.headers, json=body)

    @classmethod
    def occupy_device(cls, serial_no):
        url = 'http://{}/api/v1/user/devices'.format(cls.host)
        body = {'serial': serial_no}
        requests.post(url, headers=cls.headers, json=body)
        cls.serials.append(serial_no)



