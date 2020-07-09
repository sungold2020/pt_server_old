#!/usr/bin/bash

#查询数据库记录，会把关键词转换为条件，例如日或者japan转换为nation='日'
#支持多个条件输入，会以and连接多个条件
#
echo $#

SQL="select dirname,disk from movies where"
index=1          #定义一个计数器
if [ -z "$1" ];then              #对用户输入的参数做判断，如果未输入参数则返回脚本的用法并退出，退出值65
  echo "Usage:$0 + canshu"
  exit $number
fi

for arg in "$@"
do

  echo "arg: $index = $arg"        
  case $arg in
    "日")
        arg='nation="日"'
        ;;
    "japan")
        arg='nation="日"'
        ;;
    "韩")
        arg='nation="韩"'
        ;;   
    "korea")
        arg='nation="韩"'
        ;;           
    "国")
        arg='nation="国"'
        ;;
    "china")
        arg='nation="国"'
        ;;    
    "美")
        arg='nation="美"'
        ;;  
    "usa")
        arg='nation="美"'
        ;;          
    "印")
        arg='nation="印度"'
        ;;  
    "india")
        arg='nation="印度"'
        ;;          
    "动画")
        arg='genre like "%动画%"'
        ;;
    "anima")
        arg='genre like "%动画%"'
        ;; 
    "喜剧")
        arg='genre like "%喜剧%"'
        ;;
    "comedy")
        arg='genre like "%喜剧%"'
        ;;
    "wd4t")
        arg='disk = "wd4t"'
        ;;
    "wd2t")
        arg='disk = "wd2t"'
        ;;
    "wd2t-2")
        arg='disk = "wd2t-2"'
        ;;
    "sg3t")
        arg='disk = "sg3t"'
        ;;
    "sg8t")
        arg='disk = "sg8t"'
        ;;        
    "v")
        arg='viewed = 1'
        ;;
    "nv")
        arg='viewed = 0'
        ;;
    *)
        #RET=`expr match "$Number" "[0-9]*$"`
        if [ ${arg:0:4} == "name" ]
        then
            Name=${arg:4}
	    arg="(name like \"%$Name%\" or othernames like \"%$Name%\")"
        elif [ ${arg:0:3} == "eng" ]
        then
            EnglishName=${arg:3}
	    arg="(englishname like \"%$EnglishName%\" or foreignname like \"%$EnglishName%\")"
        elif [ `expr match "$arg" "[0-9]*$"` -gt 0 ]
        then
            arg="number = $arg "
        fi
        ;;
  esac
  echo $arg
  if [ $index -eq 1 ]
  then
        SQL="$SQL $arg"
  else
        SQL="$SQL and $arg"
  fi
    
  let index+=1
done


echo $SQL
mysql -uroot -pmoonbeam db_movies -e"$SQL"
