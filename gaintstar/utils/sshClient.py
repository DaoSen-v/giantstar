# _*_encoding=utf8_*_
# @Time : 2021/5/25 14:51 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import time

import paramiko
from paramiko import SSHClient, SFTPClient


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


class SftpClient:
    client: SFTPClient = None

    def connect(self, host, username, password, port=22):
        client = paramiko.Transport((host, port))
        client.connect(username=username, password=password)
        self.client = paramiko.SFTPClient.from_transport(client)
        return self

    def download(self, remote_path, local_path):
        self.client.get(remote_path, local_path)

    def upload(self, local_path, remote_dir):
        local_path = local_path.replace('\\', '/')
        file_name = local_path.split('/')[-1]
        remote_path = '{}/{}'.format(remote_dir.rstrip('/'), file_name)
        self.client.put(local_path, remote_path)
        return remote_path

    def close(self):
        self.client.close()


