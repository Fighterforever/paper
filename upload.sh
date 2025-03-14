#!/bin/bash

# 获取当前日期
date=$(date '+%Y%m%d')

# 进入你的本地仓库目录
cd /Users/rach/code/note

# 初始化本地仓库
git init

# 添加所有文件到本地仓库
git add .

# 提交更改
git commit -m "Initial commit"

# 添加远程仓库地址
git remote add origin https://github.com/Fighterforever/paper.git

# 从远程仓库拉取最新的更改
git pull origin master

# 创建一个新的分支
git checkout -b $date

# 推送到远程仓库
git push -u origin $date