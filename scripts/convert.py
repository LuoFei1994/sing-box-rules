#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io
import os
# ========== 强制全局UTF-8编码设置 ==========
if sys.stdout.encoding != 'UTF-8':
    # Windows环境下无法修改编码时的回退方案
    try:
        # 尝试强制设置控制台编码
        if sys.platform == "win32":
            import ctypes
            # 设置为UTF-8输出
            k32 = ctypes.windll.kernel32
            k32.SetConsoleOutputCP(65001)
        # 回退到无编码输出
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='utf-8', errors='replace', buffering=1)
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='utf-8', errors='replace', buffering=1)
    except:
        # 最终回退到ASCII
        sys.stdout = open(sys.stdout.fileno(), 'w', encoding='ascii', errors='replace', buffering=1)
        sys.stderr = open(sys.stderr.fileno(), 'w', encoding='ascii', errors='replace', buffering=1)

os.environ["PYTHONIOENCODING"] = "utf-8"
# ==========================================

import requests
import subprocess  # 添加此导入以便在环境修复中使用
# ========== 编码修复核心 ==========
# 强制设置标准输出和标准错误的编码为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')  # Python 3.7+ 特有方法
os.environ["PYTHONIOENCODING"] = "utf-8"
# =================================

# ====== 优先诊断和修复环境 ======
def fix_environment():
    # 强制修复导入环境"
    def safe_print(message):
        try:
            print(message)
        except:
            pass
    
    # 检查是否缺少requests模块
    try:
        import requests
        safe_print(f"[INFO] Requests module ready (v{requests.__version__})")
        return
    except ImportError:
        safe_print("[WARN] Requests module not found, installing...")

    # 方法1：使用系统Python安装路径（GitHub特有路径）
    system_python_path = "C:/hostedtoolcache/windows/Python/3.10.11/x64/Lib/site-packages"
    if os.path.exists(system_python_path) and system_python_path not in sys.path:
        sys.path.insert(0, system_python_path)
        safe_print(f"[ACTION] Added system path: {system_python_path}")
        
    # 方法2：安装缺失依赖
    try:
        import requests
        safe_print(f"[INFO] Imported requests from system path")
    except ImportError:
        safe_print("[ACTION] Installing requests...")
        subprocess.call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
        
    safe_print(f"[SUCCESS] Requests v{requests.__version__} ready")

# 立即执行环境修复
fix_environment()
# =================================

# 现在可以安全导入其它模块

import zipfile
import json
import time
import shutil
import subprocess

# ========== 编码修复核心 ==========
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
os.environ["PYTHONIOENCODING"] = "utf-8"
# =================================

def safe_print(message):
    #"安全的打印函数"
    try:
        print(message)
    except Exception:
        pass  # 忽略打印错误

def download_singbox():
    """下载并准备sing-box转换工具"""
    try:
        safe_print("== 开始获取sing-box最新版本信息 ==")
        response = requests.get("https://api.github.com/repos/SagerNet/sing-box/releases/latest", timeout=30)
        response.raise_for_status()
        release_data = response.json()
        version = release_data["tag_name"]
        safe_print(f"最新版本: {version}")
        
        # 查找Windows版下载链接
        download_url = None
        for asset in release_data["assets"]:
            asset_name = asset["name"].lower()
            if "windows" in asset_name and "amd64" in asset_name and "zip" in asset_name:
                download_url = asset["browser_download_url"]
                safe_print(f"匹配到资源: {asset['name']}")
                break
        
        if not download_url:
            safe_print("资源匹配失败，使用默认URL")
            download_url = f"https://github.com/SagerNet/sing-box/releases/download/{version}/sing-box-{version}-windows-amd64.zip"
        
        safe_print(f"下载URL: {download_url}")
        
        # 下载文件
        safe_print("开始下载...")
        download_response = requests.get(download_url, timeout=120)
        download_response.raise_for_status()
        
        # 保存文件
        with open("sing-box.zip", "wb") as f:
            f.write(download_response.content)
        safe_print(f"下载完成，大小: {len(download_response.content)/1024/1024:.2f} MB")
        
        # 解压文件
        safe_print("开始解压...")
        with zipfile.ZipFile("sing-box.zip", 'r') as zip_ref:
            # 创建解压目录
            extract_dir = "sing-box-temp"
            os.makedirs(extract_dir, exist_ok=True)
            zip_ref.extractall(extract_dir)
            
            # 查找可执行文件
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    if file.lower() == "sing-box.exe":
                        exe_path = os.path.join(root, file)
                        shutil.copy(exe_path, "sing-box.exe")
                        safe_print(f"找到sing-box.exe: {exe_path}")
                        break
        
        return True
        
    except Exception as e:
        safe_print(f"下载sing-box失败: {str(e)}")
        return False

def convert_rules():
    """转换规则集为SRS格式"""
    try:
        # 规则源URL
        rule_url = "https://raw.githubusercontent.com/privacy-protection-tools/anti-AD/master/anti-ad-domains.txt"
        
        # 创建build目录
        os.makedirs("build", exist_ok=True)
        
        # 下载规则
        safe_print(f"下载规则集: {rule_url}")
        response = requests.get(rule_url, timeout=60)
        response.encoding = 'utf-8'
        
        # 处理规则：转换为JSON格式
        rule_data = {"version": 1, "rules": []}
        domain_count = 0
        
        for line in response.text.splitlines():
            stripped = line.strip()
            # 跳过空行和注释
            if not stripped or stripped.startswith(('#', '!')):
                continue
            # 跳过IP地址（包含数字）
            if any(c.isdigit() for c in stripped):
                continue
            
            # 添加到规则列表
            rule_data["rules"].append({"domain": [stripped]})
            domain_count += 1
        
        safe_print(f"处理完成: 有效域名数: {domain_count}")
        
        # 保存为JSON文件
        json_path = "build\\rule.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rule_data, f, indent=2)
        safe_print(f"JSON规则文件已保存: {json_path}")
        
        # 转换命令（使用绝对路径）
        srs_path = os.path.abspath("build\\rule.srs")
        safe_print("开始转换规则为SRS格式...")
        
        # 确保使用正确的路径
        exe_path = os.path.abspath("sing-box.exe")
        cmd = f'"{exe_path}" rule-set compile "{os.path.abspath(json_path)}" -o "{srs_path}"'
        safe_print(f"执行命令: {cmd}")
        
        # 执行转换
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')
        
        # 检查结果
        if result.returncode == 0:
            if os.path.exists(srs_path):
                size_kb = os.path.getsize(srs_path) / 1024
                safe_print(f"转换成功! 文件大小: {size_kb:.2f} KB")
                return True
            else:
                safe_print("错误: 未生成SRS文件")
        else:
            safe_print(f"转换失败! 错误代码: {result.returncode}")
            safe_print(f"错误输出: {result.stderr}")
        
        return False
            
    except Exception as e:
        safe_print(f"规则转换失败: {str(e)}")
        return False

if __name__ == "__main__":
    safe_print("== 脚本启动 ==")
    safe_print(f"Python版本: {sys.version.split()[0]}")
    
    # 步骤1: 下载sing-box
    download_success = download_singbox()
    
    # 步骤2: 转换规则
    if download_success and os.path.exists("sing-box.exe"):
        safe_print("开始转换规则...")
        if convert_rules():
            safe_print("======= 所有任务完成! =======")
            sys.exit(0)
    
    safe_print("======= 任务失败! =======")
    sys.exit(1)
