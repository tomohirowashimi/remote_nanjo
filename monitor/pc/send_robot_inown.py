# // 20220217 新規作成
 
import datetime
import platform
from smb.SMBConnection import SMBConnection
import os
import shutil

print(os.getcwd())

now = datetime.datetime.now()
path_dir = "//snanf/DFS/八千代工場/ReadOnly/管理Gr/生産指示書/生産指示書/" + str(now.year) + "年/"
move_path_dir = r"C:\Users\TWashimi\Documents\washimi\washimi\⑯　monitor system\1. own\process_run"

# // 接続
conn = SMBConnection(
    'robot',
    'vehicle',
    platform.uname().node,
    'PC19022',
    domain='',
    use_ntlm_v2=True)
        
conn.connect('192.168.107.181', 139)
print(conn.echo('echo success'))

# // ファイルコピー、送信
list_file_name = os.listdir(path_dir)

for i_file_name in list_file_name:
    join_path = os.path.join(path_dir, i_file_name)
    move_path = os.path.join(move_path_dir, i_file_name)

    if os.path.isfile(join_path):
        shutil.copy(join_path, move_path)

        with open(i_file_name, 'rb') as f:
            conn.storeFile('robot', '/monitor_data/' + i_file_name, f)

conn.close()
