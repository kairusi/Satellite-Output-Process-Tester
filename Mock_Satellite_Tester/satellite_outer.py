import datetime
import os
from threading import Timer
from firebase import firebase


class SatelliteOuter(object):

    def __init__(self):
        self.satellite_firebase = firebase.FirebaseApplication('https://satellite-d94ef.firebaseio.com/', None)
        self.mode_dic = self.satellite_firebase.get('status/', None)
        for key in self.mode_dic.keys():
            if self.mode_dic[key]['state'] == 'run':
                self.satellite_firebase.put('status/' + key, 'state', 'stop')
                self.mode_dic[key]['state'] = 'stop'
            self.mode_dic[key]['thread'] = Timer

    def file_scheduling(self, str_mode):
        thread = Timer(self.mode_dic[str_mode]['interval']-0.001,
                       self.file_scheduling,
                       [str_mode])
        thread.start()
        self.mode_dic[str_mode]['thread'] = thread
        self.satellite_firebase.put('status/' + str_mode, 'state', 'run')
        self.create_file(str_mode)

    def stop_file_scheduling(self, str_mode):
        self.mode_dic[str_mode]['thread'].cancel()
        self.satellite_firebase.put('status/' + str_mode, 'state', 'stop')

    def create_file(self, str_mode):
        file_name = self.create_file_name(str_mode)
        self.check_dir(file_name)
        f = open(file_name, "w+")
        f.write(str(datetime.datetime.now()))
        f.close()
        return file_name

    def set_mode_interval(self, str_mode, interval):
        self.mode_dic[str_mode]['interval'] = int(interval)*60
        self.satellite_firebase.put('status/'+str_mode, 'interval', interval)

    def create_file_name(self, str_mode):
        file_path = "/COMS/GOCI/{:s}/%Y/%m/%d/COMS_GOCI_{:s}_%Y%m%d%H%M%S.txt"
        now_date = datetime.datetime.now()
        file_path = datetime.datetime.strftime(now_date, file_path)
        file_path = file_path.format(str_mode.upper(), str_mode.upper())
        file_pre_path = '/'.join(file_path.split('/')[:-1])
        file_name = file_path.split('/')[-1]
        self.satellite_firebase.put('satellite_dir'+file_pre_path, file_name.split('.')[0], file_name.split('.')[-1])
        return file_path

    @staticmethod
    def check_dir(path):
        path = '/'.join(path.split('/')[:-1])
        if not os.path.exists(path):
            os.makedirs(path)