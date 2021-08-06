# _*_encoding=utf8_*_
# @Time : 2021/5/25 17:11 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import re

from giantstar.utils.sshClient import CSSHClient
from giantstar.sessionManage.appSession.openstfController import OpenstfController
from giantstar.utils.error import NoAvailableDevice

class IOSCmd:
    pass
    # def ios_devices(self):
    #     ios_devices = {}
    #     wda_ports = self.wda_info()
    #     appium_hubs = self.ios_hubs()
    #     shell_result = self.client.exec_command('/usr/local/bin/idevice_id -l')
    #     lines = shell_result.split('\n')
    #     for line in lines:
    #         line = line.strip('\n')
    #         if line:
    #             serial_no = line
    #             wda_port = wda_ports.get(serial_no)
    #             appium_hub = appium_hubs.get(serial_no)
    #             ios_info = self._get_ios_info(serial_no)
    #
    #             ios_devices[serial_no] = {
    #                 'hostname': self.hostname,
    #                 'serial_no': serial_no,
    #                 'appium_hub': appium_hub,
    #                 'wda_port': wda_port,
    #                 **ios_info
    #             }
    #
    #     return ios_devices
    #
    # def ios_info(self, serial_no):
    #     tmp = {}
    #     cmd = "/usr/local/bin/ideviceinfo -u {}|grep -E 'ProductName|ProductType|ProductVersion'".format(serial_no)
    #     shell_result = self.client.exec_command(cmd)
    #     lines = shell_result.split('\n')
    #     reg_str = '([^:]*):\s*([^:]*)'
    #     for line in lines:
    #         p = re.compile(reg_str)
    #         f = p.findall(line)
    #         if len(f) > 0:
    #             key, value = f[0][0], f[0][1]
    #             tmp[key] = value
    #
    #     ios_info = {
    #         'product_name': tmp.get('ProductName'),
    #         'product_type': tmp.get('ProductType'),
    #         'product_version': tmp.get('ProductVersion')
    #     }
    #     return ios_info
    #
    # def wda_info(self):
    #     '''
    #     获取设备:ios wda-port端口
    #     :return: { 'serial_no': 'wda-port' }
    #     '''
    #     wda = {}
    #     cmd = "ps -ef|grep 'ios-device'"
    #     shell_result = self.client.exec_command(cmd)
    #     lines = shell_result.split('\n')
    #     p = re.compile(r'--serial\s*(\S+).*--wda-port\s*(\S+)')
    #     for line in lines:
    #         f = p.findall(line)
    #         if len(f) > 0:
    #             uid, wda_port = f[0][0], f[0][1]
    #             wda[uid] = wda_port
    #     return wda
    #
    # def install_ios_app(self, serial_no, remote_app_path):
    #     install_str = f'/usr/local/bin/ideviceinstaller -u {serial_no} -i {remote_app_path}'
    #     self.client.exec_command(install_str)
    #
    # # 卸载ios安装包
    # def uninstall_ios_app(self, serial_no, package_name):
    #     uninstall_str = f'/usr/local/bin/ideviceinstaller -u {serial_no} -U {package_name}'
    #     self.client.exec_command(uninstall_str)
    #
    # def ios_hub(self):
    #     '''
    #     获取设备:appium进程端口信息
    #     :return: { 'serial_no': 'appium_port' }
    #     '''
    #     hub = {}
    #     cmd = "ps -ef|grep appium|awk '{print $15,$13}'"
    #     shell_result = self.client.exec_command(cmd)
    #     lines = shell_result.split('\n')
    #     p = re.compile(r'^(\S*)\s+(\d+)$')
    #     for line in lines:
    #         f = p.findall(line)
    #         if len(f) > 0:
    #             uid, port = f[0][0], f[0][1]
    #             hub[uid] = 'http://{}:{}/wd/hub'.format(self.host, port)
    #     return hub
    #
    # def download_iso(self, app):
    #     pass


class AndroidCmd:
    appium_compile = re.compile(r'^(\S*)\s+(\d+)$')
    device_compile = re.compile(r'^(\S+)\s+device$')
    adb_path = ''
    def acquire_android_hub(self, serial):
        cmd = "ps -ef|grep appium|awk '{print $13,$11}'"
        result = self.client.exec_command(cmd)
        lines = result.split('\n')
        for line in lines:
            f = self.appium_compile.findall(line)
            uid, port = (f[0][0], f[0][1]) if f else (None, None)
            print(uid, port)
            if serial and uid == serial:
                return f'http://{self.host}:{port}/wd/hub', uid
            elif not serial:
                return f'http://{self.host}:{port}/wd/hub', uid
        raise NoAvailableDevice(f"【真机分配】无可用设备")

    def adb_command(self, cmd):
        self.client.exec_command(cmd)

    def install_apk(self, serial, apk_path):
        self.client.exec_command(f'{self.adb_path} -s {serial} install {apk_path}')

    def uninstall_apk(self, serial, package_name):
        self.client.exec_command(f'{self.adb_path} -s {serial} uninstall {package_name}')

    def download_apk(self):
        pass

class DevicesManage(AndroidCmd, CSSHClient):
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client: CSSHClient = CSSHClient.connect(
            host=host, port=port, username=username, password=password
        )

    @classmethod
    def free_device(cls):
        """获取可用设备"""
        devices = OpenstfController.devices().get("devices")
        free_android = []
        free_ios = []
        for device in devices:
            if device["ready"] and not device["using"] and not device["owner"]:
                if device["platform"] == "Android":
                    free_android.append(device["serial"])
                elif device["platform"] == "iOS":
                    free_ios.append(device["serial"])
        return free_android, free_ios

    def get_device_caps(self, platform: str, serial: str=None):
        """获取设备名称的hub端口，设备名称"""
        free_android, free_ios = self.free_device()
        if platform.lower() == "android":
            if serial and serial in free_android:
                return self.acquire_android_hub(serial)
            elif free_android:
                return self.acquire_android_hub(free_android[-1])
            else:
                raise NoAvailableDevice(f"【设备分配】Android设备已全部分配暂无空闲, 请等待设备可用后再次尝试···")
        elif platform.lower() == 'ios':
            # return self.acquire_hub(usable_serial)
            raise NoAvailableDevice(f"【设备分配】IOS设备将在后续版本添加, 请优先使用Android设备")


if __name__ == '__main__':
    from giantstar.globalSetting import plus_setting
    stf = plus_setting.OPENSTF
    host =  "stf.casstime.com"
    token =  "4cf0639896ea45cd8c40ef7bf9f4ee5c4893a753588a4f018ae69eaba2122a87"
    android_provider =  {
        "host": "10.118.80.152",
        "port": 22,
        "username": "root",
        "password": "casstime",
    }

    d = DevicesManage(**android_provider)
    OpenstfController.host = host
    OpenstfController.headers = {'Authorization': f'Bearer {token}'}
    serial = d.get_device('android')
    OpenstfController.occupy_device(serial)

    print(serial)
    d.close()