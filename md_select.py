import os
import shutil

# 获取当前目录
current_dir = os.getcwd()

# 创建新的文件夹
new_dir = os.path.join(current_dir, 'md_files')
os.makedirs(new_dir, exist_ok=True)

# 递归地获取所有的.md文件
md_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(current_dir) for f in filenames if f.endswith('.md')]

# 复制所有的.md文件到新的文件夹
for f in md_files:
    shutil.copy(f, os.path.join(new_dir, os.path.basename(f)))