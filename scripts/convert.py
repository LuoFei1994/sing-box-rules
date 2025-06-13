import os
import requests
from pathlib import Path

# 创建目录
Path("temp").mkdir(exist_ok=True)
Path("build").mkdir(exist_ok=True)

# 1. 下载最新版 sing-box
print("下载sing-box转换器...")
tools_url = "https://github.com/SagerNet/sing-box/releases/latest/download/sing-box-windows-amd64v3.zip"
tools_file = requests.get(tools_url)
with open("temp/sing-box.zip", "wb") as f:
    f.write(tools_file.content)

# 解压工具
print("解压工具...")
os.system("tar -xf temp/sing-box.zip -C temp/")

# 2. 下载并转换所有规则
with open("rules/sources.txt") as f:
    urls = f.read().splitlines()

for url in urls:
    if not url or url.startswith("#"):
        continue
        
    print(f"处理规则: {url}")
    # 提取文件名
    filename = url.split("/")[-1].replace(".txt", "")
    
    # 下载规则文本
    rule_text = requests.get(url).text
    with open(f"temp/{filename}.txt", "w", encoding="utf-8") as f:
        f.write(rule_text)
    
    # 转换规则格式
    os.system(f"temp\\sing-box.exe rule-set compile temp/{filename}.txt -o build/{filename}.srs")
    print(f"已生成: build/{filename}.srs")

print("所有规则转换完成！")
print(f"生成文件列表: {os.listdir('build')}")
