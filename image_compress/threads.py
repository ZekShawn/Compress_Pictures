#!/usr/bin/python3
import threading
import win32ui
from compress import compress_main
from copy import deepcopy


# 打开资源管理器线程
class Explorer(threading.Thread):
    def __init__(self, thread_id, thread_name, call_back):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.call_back = call_back

    def run(self):
        explorer_dialog = win32ui.CreateFileDialog(1)
        explorer_dialog.SetOFNInitialDir("默认打开路径")
        explorer_dialog.DoModal()
        file_path = explorer_dialog.GetPathName()
        file_path = "\\".join(file_path.split("\\")[:-1])
        self.call_back(file_path)


# 运行 压缩 线程
class PNG_Compress(threading.Thread):
    def __init__(self, thread_id, thread_name, call_back, args):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.thread_name = thread_name
        self.call_back = call_back
        self.args = args

    def run(self):
        try:
            pictures_exception = []
            for root_dir in self.args["root_dir"]:
                temp_args = deepcopy(self.args)
                temp_args["root_dir"] = root_dir
                temp_pictures_exception = compress_main(temp_args)
                if temp_pictures_exception is not None:
                    pictures_exception += temp_pictures_exception
            self.call_back([True, pictures_exception, None])

        except Exception as e:
            self.call_back([False, None, e])
