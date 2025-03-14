import subprocess

# 定义你的命令
command = "python translate.py --api_key 'sk-bdea629c178e4c7285378d40db186d08' --root_dir '/Users/rach/code/note/unsorted' --detail full --workers 3"

# 运行命令
subprocess.run(command, shell=True)