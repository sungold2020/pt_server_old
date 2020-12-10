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
