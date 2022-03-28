# // 20220129 関数化　→　D/N 対応　→　cell line 対応　→　IP更新

import platform
from smb.SMBConnection import SMBConnection

ip_f5 = '192.168.107.242'
ip_f6lh = '192.168.107.20'
ip_f6rh = '192.168.107.21'
ip_cell = '192.168.107.23'
file_f5_day = 'product_f5_day.csv'
file_f5_night = 'product_f5_night.csv'
file_f6_day = 'product_f6_day.csv'
file_f6_night = 'product_f6_night.csv'
file_cell_day = 'product_12_day.csv'
file_cell_night = 'product_12_night.csv'

def connect(ip, file1, file2):
    conn = SMBConnection(
        'pi',
        'silvia',
        platform.uname().node,
        'raspberry pi',
        domain='',
        use_ntlm_v2=True)
        
    conn.connect(ip, 139)
    print(conn.echo('echo success'))

    with open(file1, 'rb') as f:
        conn.storeFile('pi', file1, f)
    with open(file2, 'rb') as f:
        conn.storeFile('pi', file2, f)

    conn.close()

if __name__ == "__main__":
    connect(ip_f5, file_f5_day, file_f5_night)
    connect(ip_f6lh, file_f6_day, file_f6_night)
    connect(ip_f6rh, file_f6_day, file_f6_night)
    connect(ip_cell, file_cell_day, file_cell_night)

