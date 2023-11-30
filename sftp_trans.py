# -*- coding: utf-8 -*-
import os
import stat
import time
import paramiko
from logger import *


class sftp_rsa_access(object):
    def __init__(
        self,
        sftpserver_address,
        sftpserver_port,
        sftpclient_private_key_path,
        sftplogin_username,
        sftpclient_private_key_password=None,
        sftplogin_userpassword=None,
    ):
        self.sftpserver_address = sftpserver_address
        self.sftpserver_port = sftpserver_port

        self.sftpclient_private_key_path = sftpclient_private_key_path
        self.sftpclient_private_key_password = sftpclient_private_key_password

        self.sftplogin_username = sftplogin_username
        self.sftplogin_userpassword = sftplogin_userpassword

        self.sftpclient = ''

        self.private_key = paramiko.RSAKey.from_private_key_file(
            filename=self.sftpclient_private_key_path
        )

        self.transport = paramiko.Transport(
            (self.sftpserver_address, int(self.sftpserver_port))
        )

        self.rlogger_name = self.generate_time_stamp()
        self.rlogger = Logger(self.rlogger_name + '_' 'sftp_transfer.log', level='info')

    def generate_time_stamp(self):
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        return time_stamp

    def connect_sftpserver_with_private_key(self):
        print(
            '\nConnecting to sftpserver: %s:%s'
            % (self.sftpserver_address, self.sftpserver_port)
        )

        self.rlogger.logger.info(
            '\nConnecting to sftpserver: %s:%s'
            % (self.sftpserver_address, self.sftpserver_port)
        )

        self.transport.connect(username=self.sftplogin_username, pkey=self.private_key)

        self.sftpclient = paramiko.SFTPClient.from_transport(self.transport)
        folder_list = self.sftpclient.listdir()

        if folder_list:
            print(
                'Successflly connected to sftpserver: %s:%s'
                % (self.sftpserver_address, self.sftpserver_port)
            )
            self.rlogger.logger.info(
                'Successflly connected to sftpserver: %s:%s'
                % (self.sftpserver_address, self.sftpserver_port)
            )

            print('current_path_folder_list:%s\n' % (folder_list))
            self.rlogger.logger.info('current_path_folder_list:%s\n' % (folder_list))

    def disconnect_sftpserver(self):
        self.transport.close()

    def sftpserver_listdir(self, target_directory):
        tmp_folder_list = self.sftpclient.listdir(target_directory)
        # print('directory_list [%s]: %s' % (target_directory, tmp_folder_list))
        return tmp_folder_list

    def sftpserver_listdir_attr(self, target_directory):
        tmp_folder_list = self.sftpclient.listdir_attr(target_directory)
        print('directory_listdir_attr [%s]: %s' % (target_directory, tmp_folder_list))
        self.rlogger.logger.info(
            'directory_listdir_attr [%s]: %s' % (target_directory, tmp_folder_list)
        )
        return tmp_folder_list

    def sftpserver_lstat(self, target_directory):
        """_summary_
            similar to linux command 'ls -l'
        Args:
            target_directory (_type_): _description_
            target directory we want to stat
        Returns:
            _type_: _description_
        """
        tmp_folder_lstat = self.sftpclient.lstat(target_directory)
        print('directory_lstat [%s]: %s' % (target_directory, tmp_folder_lstat))
        self.rlogger.logger.info(
            'directory_lstat [%s]: %s' % (target_directory, tmp_folder_lstat)
        )

        return tmp_folder_lstat

    def sftpserver_posix_rename(self, target_directory, oldpath, newpath):
        self.sftpserver_chdir(target_directory)
        self.sftpclient.posix_rename(oldpath=oldpath, newpath=newpath)
        print(
            'rename_directory_list [%s]: %s'
            % (target_directory, self.sftpserver_listdir('./'))
        )
        self.rlogger.logger.info(
            'rename_directory_list [%s]: %s'
            % (target_directory, self.sftpserver_listdir('./'))
        )

    def sftpserver_chdir(self, target_directory):
        if target_directory != self.sftpserver_getcwd():
            self.sftpclient.chdir(target_directory)
        else:
            print('Already in target_directory path!\n')
            self.rlogger.logger.info('Already in target_directory path!\n')

        target_directory_folder_list = self.sftpclient.listdir()
        print('%s: %s:\n' % (target_directory, target_directory_folder_list))
        self.rlogger.logger.info(
            '%s: %s:\n' % (target_directory, target_directory_folder_list)
        )

        return target_directory_folder_list

    def sftpserver_file(self, target_directory, file_name, mode, bufsize):
        tmp_target_dir_file_list = self.sftpserver_chdir(target_directory)
        if file_name in tmp_target_dir_file_list:
            print(self.sftpclient.open(filename=file_name, mode=mode, bufsize=bufsize))

    def sftpserver_getcwd(self):
        tmp_current_dir_file_path = self.sftpclient.getcwd()
        print('current work directory: %s' % tmp_current_dir_file_path)
        self.rlogger.logger.info(
            'current work directory: %s' % tmp_current_dir_file_path
        )

        return tmp_current_dir_file_path

    def sftpserver_mkdir(self, target_directory, new_dir_name, permissions_mode):
        tmp_target_dir_file_list = self.sftpserver_chdir(target_directory)
        print('Creating directory %s' % new_dir_name)
        self.rlogger.logger.info('Creating directory %s' % new_dir_name)

        tmp_current_dir_file_list = self.sftpclient.listdir(target_directory)
        if new_dir_name in tmp_current_dir_file_list:
            print('new directory already exists!\n')
            self.rlogger.logger.info('new directory already exists!\n')
        else:
            self.sftpclient.mkdir(new_dir_name, permissions_mode)
            tmp_current_dir_file_list = self.sftpclient.listdir(target_directory)
            print('Current directory list: %s' % tmp_current_dir_file_list)
            self.rlogger.logger.info(
                'Current directory list: %s' % tmp_current_dir_file_list
            )
            if new_dir_name in tmp_current_dir_file_list:
                print('\nSuccessfully to create directory: %s\n' % new_dir_name)
                self.rlogger.logger.info(
                    '\nSuccessfully to create directory: %s\n' % new_dir_name
                )

    def sftpserver_posix_rename(self, target_directory, oldpath, newpath):
        self.sftpserver_chdir(target_directory)
        self.sftpclient.posix_rename(oldpath=oldpath, newpath=newpath)
        print(
            'rename_directory_list [%s]: %s'
            % (target_directory, self.sftpserver_listdir('./'))
        )
        self.rlogger.logger.info(
            'rename_directory_list [%s]: %s'
            % (target_directory, self.sftpserver_listdir('./'))
        )

    def sftpserver_filepath_ISDIR(self, remote_path):
        tmp_stat = self.sftpclient.stat(remote_path)
        # print('stat: %s' % tmp_stat)

        tmp_stat_stmode = tmp_stat.st_mode
        # print('st_mode: %s\n' % tmp_stat_stmode)

        if stat.S_ISDIR(tmp_stat_stmode):
            # print('%s is a directory!' % file_remote_path)
            return True
        else:
            # print('%s is not a directory!' % file_remote_path)
            return False

    def local_filepath_ISDIR(self, local_abs_path):
        tmp_stat_stmode = os.stat(local_abs_path).st_mode
        # print('st_mode: %s\n' % tmp_stat_stmode)

        if stat.S_ISDIR(tmp_stat_stmode):
            # print('%s is a directory!' % file_local_abs_path)
            return True
        else:
            # print('%s is not a directory!' % file_local_abs_path)
            return False

    def sftpserver_put_callback(self, completed_transfer_bytes, total_transfer_bytes):
        print(
            "transfer_bytes: %d/%d" % (completed_transfer_bytes, total_transfer_bytes)
        )
        self.rlogger.logger.info(
            "transfer_bytes: %d/%d" % (completed_transfer_bytes, total_transfer_bytes)
        )

        if completed_transfer_bytes != total_transfer_bytes:
            print("file transfer failed!\n")
            self.rlogger.logger.info("file transfer is going!\n")
        else:
            print('file transfer successfully!\n')
            self.rlogger.logger.info('file transfer successfully!\n')

    def sftpserver_put_singlefile(self, file_local_abs_path, remote_folder_path):
        tmp_file_name = file_local_abs_path
        tmp_file_name_split = tmp_file_name.split('/')
        file_name = tmp_file_name_split[len(tmp_file_name_split) - 1]
        print('file transfering: %s' % (file_local_abs_path))
        self.rlogger.logger.info('file transfering: %s' % (file_local_abs_path))

        tmp_dir_file_list = self.sftpserver_listdir(remote_folder_path)
        if file_name in tmp_dir_file_list:
            print('%s already exists in %s!\n' % (file_name, remote_folder_path))
            self.rlogger.logger.info(
                '%s already exists in %s!\n' % (file_name, remote_folder_path)
            )

        else:
            self.sftpclient.put(
                localpath=file_local_abs_path,
                remotepath=remote_folder_path + '/' + file_name,
                callback=self.sftpserver_put_callback,
                confirm=True,
            )

    def sftpserver_put_folder(self, local_folder_abs_path, remote_folder_path):
        tmp_local_path_file_list = os.listdir(local_folder_abs_path)
        print('local path file list: %s' % (tmp_local_path_file_list))
        self.rlogger.logger.info(
            'local path file list: %s' % (tmp_local_path_file_list)
        )

        tmp_remote_path_file_list = self.sftpserver_listdir(remote_folder_path)
        print('remote path file list: %s\n' % (tmp_remote_path_file_list))
        self.rlogger.logger.info(
            'remote path file list: %s\n' % (tmp_remote_path_file_list)
        )

        for file_name in tmp_local_path_file_list:
            print(file_name)

            # should be regular file name
            if file_name not in tmp_remote_path_file_list:
                self.sftpserver_put_singlefile(
                    local_folder_abs_path + './' + file_name, remote_folder_path
                )
            else:
                print('%s already exists in remote path file list\n' % (file_name))
                self.rlogger.logger.info(
                    '%s already exists in remote path file list\n' % (file_name)
                )

    def sftpserver_put(self, local_abs_path, remote_path):
        if not self.sftpserver_filepath_ISDIR(remote_path=remote_path):
            print('Error: %s is not a directory!' % remote_path)
            self.rlogger.logger.info('Error: %s is not a directory!' % remote_path)
        else:
            if not self.local_filepath_ISDIR(local_abs_path=local_abs_path):
                self.sftpserver_put_singlefile(local_abs_path, remote_path)
            else:
                self.sftpserver_put_folder(local_abs_path, remote_path)

    def sftpserver_get_callback(self, completed_received_bytes, total_receive_bytes):
        print(
            "receiving_bytes: %d/%d" % (completed_received_bytes, total_receive_bytes)
        )
        self.rlogger.logger.info(
            "receiving_bytes: %d/%d" % (completed_received_bytes, total_receive_bytes)
        )

        if completed_received_bytes != total_receive_bytes:
            print("file receive not complete!\n")
            self.rlogger.logger.info("file receive is going!\n")
        else:
            print('file receive successfully!\n')
            self.rlogger.logger.info('file receive successfully!\n')

    def sftpserver_get_singlefile(self, file_remote_path, local_folder_abs_path):
        tmp_file_name = file_remote_path
        tmp_file_name_split = tmp_file_name.split('/')
        file_name = tmp_file_name_split[len(tmp_file_name_split) - 1]
        print('file receiving: %s' % (file_remote_path))
        self.rlogger.logger.info('file receiving: %s' % (file_remote_path))

        tmp_dir_file_list = os.listdir(local_folder_abs_path)
        if file_name in tmp_dir_file_list:
            print('%s already exists in %s!\n' % (file_name, local_folder_abs_path))
            self.rlogger.logger.info(
                '%s already exists in %s!\n' % (file_name, local_folder_abs_path)
            )
        else:
            self.sftpclient.get(
                remotepath=file_remote_path,
                localpath=local_folder_abs_path + '/' + file_name,
                callback=self.sftpserver_get_callback,
            )

    def sftpserver_get_folder(self, remote_folder_path, local_folder_abs_path):
        tmp_local_path_file_list = os.listdir(local_folder_abs_path)
        print('local path file list: %s' % (tmp_local_path_file_list))
        self.rlogger.logger.info(
            'local path file list: %s' % (tmp_local_path_file_list)
        )

        tmp_remote_path_file_list = self.sftpserver_listdir(remote_folder_path)
        print('remote path file list: %s\n' % (tmp_remote_path_file_list))
        self.rlogger.logger.info(
            'remote path file list: %s\n' % (tmp_remote_path_file_list)
        )

        for file_name in tmp_remote_path_file_list:
            # should be regular file name
            if file_name not in tmp_local_path_file_list:
                self.sftpserver_get_singlefile(
                    remote_folder_path + './' + file_name, local_folder_abs_path
                )
            else:
                print('%s already exists in local path file list\n' % (file_name))
                self.rlogger.logger.info(
                    '%s already exists in local path file list\n' % (file_name)
                )

    def sftpserver_get(self, remote_path, local_abs_path):
        if not self.local_filepath_ISDIR(local_abs_path):
            print('Error: %s is not a directory!' % local_abs_path)
            self.rlogger.logger.info('Error: %s is not a directory!' % local_abs_path)
        else:
            if not self.sftpserver_filepath_ISDIR(remote_path):
                self.sftpserver_get_singlefile(remote_path, local_abs_path)
            else:
                self.sftpserver_get_folder(remote_path, local_abs_path)


if __name__ == "__main__":
    sftp_rsa_access = sftp_rsa_access(
        'ip_address',
        port,
        './id_rsa',
        username,
    )

    sftp_rsa_access.connect_sftpserver_with_private_key()

    sftp_rsa_access.sftpserver_get(
        remote_folder_path,
        local_abs_path,
    )

    sftp_rsa_access.disconnect_sftpserver()
