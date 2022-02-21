import os
import jpype
from PIL import Image


# 获取文件路径
def get_pictures_dir(root_dir, picture_direc, compress_tag, picture_type):

    # 获取目录下的文件名
    dirs = os.listdir(root_dir)
    for direc in dirs:

        # 连接得到全路径
        direc = os.path.join(root_dir, direc)

        # 如果是路径
        if not os.path.isfile(direc):

            # 循环查找
            get_pictures_dir(direc, picture_direc, compress_tag, picture_type)

        # 如果是文件
        else:
            for p_type in picture_type:
                if (p_type in direc) and (compress_tag not in direc):
                    picture_direc.append(direc)


# 使用pillow压缩图片
def pillow_compress_png(
        file, compress_tag, compress_size, quality=95, inplace=False, is_resize=False, height=None, width=None):

    # 如果图片被处理过
    if compress_tag in file:
        print(f"{file}  图片已被处理 {os.path.getsize(file) // 1024}")
        return

    # 打开图片
    image = Image.open(file)
    out_file = f"{file[:-4]}{compress_tag}.png"

    # 如果图片本身满足大小
    if (os.path.getsize(file) / 1024) <= compress_size:
        print(f"{file}  图片无需处理 {os.path.getsize(file)//1024}")
        return

    # 如果需要进行像素拉伸
    if is_resize:
        assert width is not None
        if height is None:
            height = int(image.height / image.width * width)
        pre_size = os.path.getsize(file)
        image = image.resize((width, height), Image.ANTIALIAS)
        image.save(f"{out_file[:-4]}_resize.png", "PNG")
        print(f"{file}  {pre_size//1024}->{os.path.getsize(file)//1024}  像素: {image.height, image.width}, ")

    # 如果大小不满足要求，进行 RGB 改变
    if os.path.getsize(file) / 1024 > compress_size:
        image = image.convert("RGB")
        image.save(out_file, "PNG", quality=quality)

    # 如果大小还不能满足要求 进一步改变通道
    if (os.path.getsize(out_file) / 1024) > compress_size:
        image.quantize(colors=256, method=0)
        image.save(out_file, "PNG")

    # 依然无法满足需求，返回
    if (os.path.getsize(out_file) / 1024) > compress_size:
        if inplace:
            os.remove(file)
            os.rename(out_file, file)
            if os.path.exists(f"{out_file[:-4]}_resize.png"):
                os.remove(f"{out_file[:-4]}_resize.png")
        return file

    # 打印最终的处理结果
    print(f"{file}  {os.path.getsize(file)//1024}->{os.path.getsize(out_file)//1024}")

    # 直接替换原来的文件
    if inplace:
        os.remove(file)
        os.rename(out_file, file)
        if os.path.exists(f"{out_file[:-4]}_resize.png"):
            os.remove(f"{out_file[:-4]}_resize.png")


# 压缩图片
def compress_pictures(picture_direc, compress_tag, compress_size, inplace, is_resize, height, width):

    # 无法被压缩成功的图片收集
    exception_pictures = []

    # 循环对所有图片进行压缩
    for file in picture_direc:

        # 压缩图片
        failed_picture = pillow_compress_png(
            file, compress_tag=compress_tag, compress_size=compress_size,
            inplace=inplace, height=height, width=width, is_resize=is_resize
        )

        # 无法达到要求的图片收集
        if failed_picture is not None:
            exception_pictures.append(failed_picture)

    # 打印输出无法被压缩的图片
    print(f"很遗憾，仍然有下面的图片无法被压缩：")
    for file in exception_pictures:
        print(file)


# Java 压缩PNG
def java_compress_png(jar_dir, args):

    # jar 路径的创建
    jar_path = os.path.join(os.path.abspath("."), jar_dir)

    # 创建类
    CompressPictures = jpype.JClass("com.zeksay.CompressPictures")

    # 调用方法
    picture_exception = CompressPictures.compressPictures(args)

    # 返回异常图片
    return picture_exception


# 压缩主函数
def compress_main(args):

    # 是否本地更改
    inplace = args['inplace']

    # 是否需要调整尺寸
    is_resize = args['is_resize']

    # 尺寸要求
    height = args['height']
    width = args['width']

    # 扫描图片类型
    picture_type = args['pictures_type']

    # 图片根目录
    root_dir = args['root_dir']

    # 压缩图片 处理标识
    compress_tag = args['compress_tag']

    # 压缩后的图片大小
    compress_size = args['compress_size']

    # 获取图片地址
    picture_direc = []
    get_pictures_dir(root_dir, picture_direc, compress_tag, picture_type)

    # 处理图片
    compress_pictures(
        picture_direc, compress_tag=compress_tag, compress_size=compress_size,
        inplace=inplace, is_resize=is_resize, height=height, width=width
    )

    # 打印日志
    print("----------------------split line----------------------")
    print("转由Java处理：")

    # Java 压缩
    jar_dir = args['jar_dir']
    picture_exception = java_compress_png(jar_dir, [compress_tag, f"{compress_size}", root_dir])
    if len(picture_exception) < 1:
        picture_exception = None
    return picture_exception


if __name__ == "__main__":
    args = {
        "inplace": True,
        "is_resize": True,
        "height": None,
        "width": 600,
        "pictures_type": [".png", ".tif"],
        "root_dir": "E:\\兴趣爱好\\压缩图片\\image-compress-python\\pictures",
        "compress_tag": "_compressed",
        "compress_size": 500,
        "jar_dir": "jar\\image-compress-java.jar"
    }
    compress_main(args)
