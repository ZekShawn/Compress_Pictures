# GUI 库
import os
import json
import jpype
import ctypes
import tkinter
from tkinter import *
from tkinter.messagebox import askquestion, showerror, showinfo

# 逻辑执行库
from threads import *


class Compress:
    def __init__(self):

        # 参数设置
        font_size = 12
        self.folder_path = None

        # 窗口初始化
        self.root = Tk()
        self.if_open_explorer = False
        self.root.iconphoto(True, tkinter.PhotoImage(file=os.path.join(os.path.abspath("."), "icon.png")))
        self.root.title("批量压缩图片（PNG）")

        # 设置高DPI缩放设置
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        self.root.tk.call('tk', 'scaling', scale_factor/75)

        # 设置窗口居中显示
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        h, w = hs//2, ws//2
        self.root.geometry('%dx%d+%d+%d' % (w, h, ws/2.5, hs/2.5))

        # 标签
        self.mode_label = Label(
            self.root, text="图片压缩模式：",
            height=2, width=15,
            font=('宋体', font_size)
        )
        self.inplace_mode_label = Label(
            self.root, text="图片修改模式：",
            height=2, width=15,
            font=('宋体', font_size)
        )
        self.size_label = Label(
            self.root, text="文件限制(KB)：",
            height=2, width=15,
            font=('宋体', font_size)
        )
        self.pixel_label = Label(
            self.root, text="像素(宽x高)：",
            height=2, width=15,
            font=('宋体', font_size)
        )
        self.folder_label = Label(
            self.root, text="文件所在目录：",
            height=2, width=15,
            font=('宋体', font_size)
        )

        # 按钮
        self.confirm_button = Button(
            self.root, text="开始压缩",
            command=self.confirm_compress,
            height=2, width=10,
            font=('宋体', font_size),
        )
        self.explorer_button = Button(
            self.root, text="···",
            command=self.open_explorer,
            height=1, width=5,
            font=('宋体', font_size-4),
        )
        self.quit_button = Button(
            self.root, text="退出程序",
            command=self.quit_compress,
            height=2, width=10,
            font=('宋体', font_size),
        )
        self.set_param_button = Button(
            self.root, text="加载配置",
            command=self.param_set,
            height=2, width=10,
            font=('宋体', font_size),
        )

        # 选项按钮 -  模式选择
        self.compress_mode = IntVar()
        self.normal_radio_button = Radiobutton(
            self.root, text="普通模式",
            height=2, width=10,
            font=('宋体', font_size),
            value=1,
            variable=self.compress_mode,
            command=self.set_mode
        )
        self.width_radio_button = Radiobutton(
            self.root, text="宽度模式",
            height=2, width=10,
            font=('宋体', font_size),
            value=2,
            variable=self.compress_mode,
            command=self.set_mode
        )
        self.compress_radio_button = Radiobutton(
            self.root, text="仅压缩模式",
            height=2, width=10,
            font=('宋体', font_size),
            value=3,
            variable=self.compress_mode,
            command=self.set_mode
        )

        # 选项按钮 -  图片修改
        self.inplace_mode = IntVar()
        self.inplace_radio_button = Radiobutton(
            self.root, text="直接替换",
            height=2, width=10,
            font=('宋体', font_size),
            value=1,
            variable=self.inplace_mode,
        )
        self.not_inplace_radio_button = Radiobutton(
            self.root, text="保留原图",
            height=2, width=10,
            font=('宋体', font_size),
            value=2,
            variable=self.inplace_mode,
        )

        # 输入框 - 像素大小
        self.picture_pixel_entry = Entry(
            self.root, width=30,
            font=('宋体', font_size),
        )
        # 输入框 - 文件大小
        self.picture_size_entry = Entry(
            self.root, width=30,
            font=('宋体', font_size),
        )
        # 输入框 - 文件地址
        self.folder_entry = Entry(
            self.root, width=30,
            font=('宋体', font_size),
        )

        # 控件布局
        # 压缩模式选择 - compress_mode
        self.mode_label.grid(row=2, column=1, sticky="E")
        self.normal_radio_button.grid(row=1, column=2, sticky="W")
        self.width_radio_button.grid(row=2, column=2, sticky="W")
        self.compress_radio_button.grid(row=2, column=3, sticky="W")

        # 修改模式选择 - inplace
        self.inplace_mode_label.grid(row=4, column=1, sticky="E")
        self.inplace_radio_button.grid(row=4, column=2, sticky="W")
        self.not_inplace_radio_button.grid(row=4, column=3, sticky="NW")

        # 像素大小选择 - height x width
        self.pixel_label.grid(row=5, column=1, sticky="E")
        self.picture_pixel_entry.grid(row=5, column=2, sticky="W")

        # 图片大小输入 - compress_size
        self.size_label.grid(row=6, column=1, sticky="E")
        self.picture_size_entry.grid(row=6, column=2, sticky="W")

        # 压缩文件夹所在路径 - root_dir
        self.folder_label.grid(row=7, column=1, sticky="E")
        self.folder_entry.grid(row=7, column=2, sticky="W")
        self.explorer_button.grid(row=7, column=3, sticky="W")

        # 确认按钮 - 退出按钮
        self.set_param_button.grid(row=8, column=1, sticky="E")
        self.confirm_button.grid(row=8, column=2, sticky="NW")
        self.quit_button.grid(row=8, column=3, sticky="NW")

        # 窗口运行
        self.root.mainloop()

    def confirm_compress(self):

        # 如果布尔参数未选定
        if self.compress_mode.get() < 1 or self.inplace_mode.get() < 1:
            showinfo("提示", "参数未输入完整")
            return

        # 如果压缩大小参数未选定
        if len(self.picture_size_entry.get()) < 1:
            showinfo("提示", "参数未输入完整")
            return
        compress_size = int(self.picture_size_entry.get())

        # 布尔参数初始化
        is_resize, inplace = False, False
        if self.compress_mode.get() != 3:
            is_resize = True
        if self.inplace_mode.get() == 1:
            inplace = True

        # 像素大小初始化
        pixels = self.picture_pixel_entry.get().split("x")
        height, width = None, None
        if len(pixels) > 1 and self.compress_mode.get() == 1:
            height, width = int(pixels[1]), int(pixels[0])
        else:
            width = int(pixels[0])

        # 地址初始化
        root_dir = self.folder_entry.get().split(";")
        root_dir = [x for x in root_dir if len(x) > 0]

        # 参数字典
        args = {
            "inplace": inplace,
            "is_resize": is_resize,
            "height": height,
            "width": width,
            "pictures_type": [".png", ".tif"],
            "root_dir": root_dir,
            "compress_tag": "_compressed",
            "compress_size": compress_size,
            "jar_dir": os.path.join(os.path.abspath("."), "jar/image-compress-java.jar")
        }

        # 启动 JVM
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(), "-ea", f"-Djava.class.path={args['jar_dir']}")

        # 压缩进程创建
        if_compress = askquestion("提示", "是否开始压缩？")
        if if_compress == "yes":
            self.confirm_button["text"] = "正在压缩"
            self.confirm_button.config(state=DISABLED)
            compress = PNG_Compress(2, "压缩PNG", self.compress_thread, args)
            compress.setDaemon(True)
            compress.start()

        # 保存本次参数字典
        if_save_config = askquestion("提示", "是否保存配置？")
        if if_save_config == "yes":
            if len(pixels) > 1:
                args["height"] = int(pixels[1])
            json_str = json.dumps(args, indent=4)
            with open(os.path.join(os.path.abspath("."), "config/config.json"), 'w') as config:
                config.write(json_str)

    def open_explorer(self):
        explorer = Explorer(1, "Explorer", self.explorer_thread)
        explorer.setDaemon(True)
        explorer.start()

    def set_mode(self):
        if self.compress_mode.get() == 3:
            self.picture_pixel_entry.config(state=DISABLED)
            self.picture_pixel_entry.delete("0", "-1")
        else:
            self.picture_pixel_entry.config(state=NORMAL)

    def quit_compress(self):
        # 关闭 JVM
        if jpype.isJVMStarted():
            jpype.shutdownJVM()
        self.root.destroy()

    def explorer_thread(self, file_path):
        self.folder_entry.insert("0", f"{file_path};")

    def compress_thread(self, args):
        if args[0]:
            if args[1] is not None:
                with open(os.path.join(os.path.abspath("."), "Exception.txt"), 'w') as f:
                    for picture_dir in args[1]:
                        f.writelines(picture_dir)
                showinfo("提示", "部分文件无法被压缩至指定大小，已保存为Exception.txt")
            else:
                showinfo("提示", "压缩完成")
        else:
            showerror("压缩程序出错", args[2])
        self.confirm_button["text"] = "开始压缩"
        self.confirm_button.config(state=NORMAL)

    def param_set(self):
        if os.path.exists(os.path.join(os.path.abspath("."), "config/config.json")):
            with open(os.path.join(os.path.abspath("."), "config/config.json"), 'r') as f:
                config = json.load(f)

            # 提示是否加载历史配置
            if_load_last = askquestion("加载历史配置", "是否加载上次设定？")
            if if_load_last == "yes":

                # 清除文本框
                self.picture_pixel_entry.delete("0", "end")
                self.folder_entry.delete("0", "end")
                self.picture_size_entry.delete("0", "end")

                # 设置是否本地修改
                if config['inplace']:
                    self.inplace_mode.set(1)
                else:
                    self.inplace_mode.set(2)

                # 设置是否进行缩放
                if not config['is_resize']:
                    self.compress_mode.set(3)
                else:
                    self.compress_mode.set(2)

                # 设置宽高像素
                if (config["width"] is not None) and (config["height"] is not None):
                    self.picture_pixel_entry.insert("0", f"{config['width']}x{config['height']}")
                elif config["width"] is not None:
                    self.picture_pixel_entry.insert("0", f"{config['width']}")

                # 设置文件大小
                if config["compress_size"] is not None:
                    self.picture_size_entry.insert("0", config["compress_size"])

                # 设置文件地址
                if config["root_dir"] is not None:
                    path = ";".join(config["root_dir"])
                    self.folder_entry.insert("0", f"{path};")
        else:
            showinfo("加载历史配置", "未检测到历史配置")


if __name__ == "__main__":
    Compress()
