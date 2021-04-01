#!/usr/bin/python3
# coding=utf-8
import sys
sys.path.append("..")
from movie import *
import os

def update_size(disk_path):
    for dir_name in os.listdir(disk_path):
        if not os.path.isdir(os.path.join(disk_path,dir_name)): 
            print(f"{dir_name} is not dir")
            continue

        movie = Movie(disk_path,dir_name,"wd12t")
        if not movie.check_dir_name():
            print(f"{dir_name} check_dir_name failed")
            continue

        if movie.collection == 1:
            update_size(os.path.join(disk_path,dir_name))
            continue

        if movie.number <= 0:
            print(f"{dir_name} number < 0")
            continue

        if movie.total_size == 0:
            print(f"{dir_name} can't get total_size")
            continue

        db_movie = Movie.from_db(movie.number,movie.copy,0)
        if db_movie is None:
            exec_log(f"db_movie is null")
            continue

        #if db_movie.dir_name != movie.dir_name:
        #    ExecLog(f"db_movie{db_movie.dir_name} is diff:{dir_name}")
        #    continue
        if update("update movies set size = %s where number = %s and copy = %s and size=0",(movie.total_size, movie.number, movie.copy)):
            print(f"{dir_name} update successful:{movie.total_size}")
        else:
            print(f"{dir_name} failed to update")

update_size("/media/root/WD12T")
