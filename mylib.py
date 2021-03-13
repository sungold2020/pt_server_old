import os 
import shutil
import ctypes
import platform


def add_slash(dir_name):
    """
    检查目录名是否以/结尾，否则添加结尾/
    """
    dir_name = dir_name.strip() 
    if dir_name[-1:] != '/': 
        return dir_name + "/"
    else:
        return dir_name


def remove_slash(dir_name):
    """
    检查目录名是否以/结尾，否则移除/
    """
    dir_name = dir_name.strip() 
    if dir_name[-1:] == '/': 
        return dir_name[:-1]
    else:
        return dir_name


def get_free_size(dir_name):
    if platform.system() == "Windows":
        # TODO 
        # print("暂不支持windows")
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(dir_name), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024 // 1024
    elif platform.system() == "Linux":
        t_bt_stat = os.statvfs(dir_name)
        return (t_bt_stat.f_bavail * t_bt_stat.f_frsize) / (1024 * 1024 * 1024)
    else:
        print(f"不支持的操作系统{platform.system()}")
        return 0


def get_last_lines(inputfile, n):
    dat_file = open(inputfile, 'r')
    lines = dat_file.readlines()
    count = len(lines)
    if count < n:
        n = count
    last_lines = []
    for i in range(n):
        index = count-n+i
        last_line = lines[index].strip()
        last_lines.append(last_line)
    dat_file.close()
    return last_lines


OVERWRITE = 1
IGNORE = 2
RENAME = 3


def split(src):
    """
    分离src为dir_name, file_name
    """
    if os.path.isdir(src):
        return src, ""

    return os.path.split(src)


def copyfile(src_file_name, dest, mode=IGNORE):
    """
    将src_file_name复制到dest_file_name
    src_file_name: 带路径的文件名
    dest_file_name: 带路径的文件名
    mode: 遇到重名的文件的处理方式
        OVERWRITE: 覆盖
        IGNORE: 忽略
        RENAME: 重命名，将dest_dir下的文件重命名为*.copy
    """
    if not os.path.isfile(src_file_name):
        print(f"error:执行copyfile失败,源{src_file_name}不是文件")
        return False

    dest_dir, dest_file_name = split(dest)
    # dest_dir 空代表当前目录，非空的话，目录必须存在
    if dest_dir != "" and not os.path.isdir(dest_dir):
        print(f"error:执行copyfile失败,目标文件夹{dest_dir}不存在 ")
        return False
    if dest_file_name == "":    # 目标是文件夹, 则需要加上src_file_name
        dir_name, file_name = split(src_file_name)
        dest_file_name = file_name
    dest_full_file_name = os.path.join(dest_dir, dest_file_name)

    # 判断目标是否已经存在
    if os.path.exists(dest_full_file_name):
        # 忽略
        if mode == IGNORE:
            # print(f"ignore:{src_file_name},目标文件夹已经存在相同名字的文件")
            return True
        # 重命名
        elif mode == RENAME:
            try:
                os.rename(dest_full_file_name, dest_full_file_name+".bak")
            except Exception as err:
                print(err)
                print(f"error:copyfile中执行rename({dest_full_file_name}, {dest_full_file_name}.bak)失败")
                return False
        # 覆盖
        elif mode == OVERWRITE:
            try:
                os.remove(dest_full_file_name)
                print(f"覆盖文件{dest_full_file_name}")
            except Exception as err:
                print(err)
                print(f"error:copyfile中执行remove({dest_full_file_name})失败")
                return False
        else:
            print("error:copyfile中不识别的mode")
            return False

    # 复制操作
    try:
        shutil.copyfile(src_file_name, dest_full_file_name)
    except Exception as err:
        print(err)
        print(f"error:copyfile中执行shutil.copyfile({src_file_name}, {dest_full_file_name})失败")
        return False
    return True


def copylink(src_link, dest_dir, mode=IGNORE):
    """
    复制链接到目标文件夹
    """
    if not os.path.islink(src_link):
        print(f"error:copylink, 源{src_link}不是链接")
        return False
    if not os.path.isdir(dest_dir):
        print(f"error:copylink, 目标{dest_dir}不是目录")
        return False

    dir_name, file_name = split(src_link)
    dest_file_name = os.path.join(dest_dir, file_name)
    # 目标已经存在同名的文件
    if os.path.exists(dest_file_name):
        # 不是链接就返回错误
        if not os.path.islink(dest_file_name):
            print(f"error:copylink, 目标{dest_file_name}存在且不是链接")
            return False

        # 是链接的话，则根据mode进行忽略/覆盖/重命名等操作
        # 忽略
        if mode == IGNORE:
            # print(f"ignore:{src_file_name},目标文件夹已经存在相同名字的链接")
            return True
        # 重命名
        elif mode == RENAME:
            try:
                os.rename(dest_file_name, dest_file_name+".bak")
            except Exception as err:
                print(err)
                print(f"error:copylink中执行rename({dest_file_name}, {dest_file_name}.bak)失败")
                return False
        # 覆盖
        elif mode == OVERWRITE:
            try:
                os.remove(dest_file_name)
                print(f"覆盖链接{dest_file_name}")
            except Exception as err:
                print(err)
                print(f"error:copylink中执行remove({dest_file_name})失败")
                return False
        else:
            print("error:copylink中不识别的mode")
            return False

    # 在目标文件夹中执行link操作
    link_dest = os.readlink(src_link)
    try:
        os.symlink(link_dest, dest_file_name)
    except Exception as err:
        print(err)
        print(f"error:copylink, 执行symlin({link_dest}, {dest_file_name})失败")
        return False
    return True


def copydir(src_dir, dest_dir, mode=IGNORE):
    """
    将src_dir目录下的文件(含子文件夹)拷贝到dest_dir
    """

    # 源必须为文件夹
    if not os.path.isdir(src_dir):
        print(f"error:copydir, 源{dest_dir}不是文件夹")
        return False
    # 目标必须为文件夹
    if not os.path.isdir(dest_dir):
        print(f"error:copydir, 目标{dest_dir}不是文件夹")
        return False

    # 逐一进行复制
    for file_name in os.listdir(src_dir):
        full_file_name = os.path.join(src_dir, file_name)
        # 注意link本身也可能是file或者dir，所以link要第一个判断
        if os.path.islink(full_file_name):
            if not copylink(full_file_name, dest_dir, mode):
                return False
        elif os.path.isdir(full_file_name):
            src_sub_dir = os.path.join(src_dir, file_name)
            dest_sub_dir = os.path.join(dest_dir, file_name)
            # 先在dest_dir下创建子文件夹
            if not os.path.exists(dest_sub_dir):
                try:
                    os.mkdir(dest_sub_dir)
                except Exception as err:
                    print(err)
                    print(f"error:copydir, 创建子文件夹{dest_sub_dir}失败")
                    return False
            # 拷贝整个子目录
            if not copydir(src_sub_dir, dest_sub_dir, mode):
                return False
        elif os.path.isfile(full_file_name):
            if not copyfile(full_file_name, dest_dir, mode):
                return False
        else:
            print(f"error:copydir, 不识别的文件类型{full_file_name}")
            return False
    return True


def copy(src_dir, dest_dir, mode=IGNORE):
    """
    将src_dir下的文件复制到dest_dir
    mode: 遇到重名的文件的处理方式
        OVERWRITE: 覆盖
        IGNORE: 忽略
        RENAME: 重命名，将dest_dir下的文件重命名为*.copy
    """

    if not os.path.exists(src_dir):
        print(f"error:copy, 源{src_dir}不存在")
        return False

    # 注意link本身也可能是file或者dir，所以link要第一个判断
    # 源是link
    if os.path.islink(src_dir):
        return copylink(src_dir, dest_dir, mode)
    # 源是文件夹
    elif os.path.isdir(src_dir):
        return copydir(src_dir, dest_dir, mode)
    # 源是文件
    elif os.path.isfile(src_dir):
        return copyfile(src_dir, dest_dir, mode)
    else:
        print(f"error:copy, 源{src_dir}的文件类型未知")
        return False
