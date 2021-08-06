# _*_encoding=utf8_*_
# @Time : 2021/5/25 14:51 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import time

import paramiko
from paramiko import SSHClient


class CSSHClient:
    client: SSHClient = None
    @classmethod
    def connect(cls, host, port, username, password):
        """与远程服务器简历ssh连接"""
        cls.client  = paramiko.SSHClient()
        cls.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cls.client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password
        )
        return cls

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()

    @classmethod
    def exec_command(cls, cmd, **kwargs):
        stdin, stdout, stderr = cls.client.exec_command(cmd, **kwargs)
        result = stdout.read()
        result = str(result, encoding='utf-8')
        return result

    @classmethod
    def move_dir(cls, filepath, target):
        cmd = f'mv -f {filepath} {target}'
        cls.exec_command(cmd)

    @classmethod
    def wait_file_exits(cls, filepath, timeout=30):
        sftp = cls.client.open_sftp()
        while timeout:
            try:
                sftp.stat(filepath)
                break
            except IOError:
                timeout -= 1
                time.sleep(1)
        sftp.close()



