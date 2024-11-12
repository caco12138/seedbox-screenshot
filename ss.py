import os
import sys
import shutil
import subprocess
import platform
import random
import concurrent.futures
import urllib.request
import tarfile
import warnings
import requests

warnings.filterwarnings("ignore", category=DeprecationWarning)

# 通用错误处理函数
def handle_error(message, exception):
    print(f"\033[31m{message}: {exception}\033[0m")
    sys.exit(1)

def check_program_installed(program):
    """ 检查指定程序是否安装。 """
    return shutil.which(program) is not None

def download_file(url, output_path):
    """ 下载文件并保存到指定路径。 """
    try:
        print(f"正在下载 {url}...")
        urllib.request.urlretrieve(url, output_path)
        print(f"下载完成")
    except Exception as e:
        handle_error("下载失败", e)

def extract_archive(file_path, extract_to):
    """ 解压缩下载的文件，并避免DeprecationWarning。 """
    with tarfile.open(file_path, 'r:gz') as tar:
        tar.extractall(path=extract_to, filter=lambda member: member)

def install_oxipng():
    """ 自动检测 Linux 平台并安装合适的 oxipng 版本，仅支持 x86_64 架构。 """
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system != "linux":
        print("\033[31m此安装脚本仅支持 Linux 系统。\033[0m")
        sys.exit(1)

    if arch == "aarch64":
        print("\033[31m当前架构为 ARM (aarch64)，暂不支持一键安装 oxipng。\033[0m")
        sys.exit(1)

    if arch != "x86_64":
        print(f"\033[31m未找到适用于 {arch} 架构的 oxipng 版本。\033[0m")
        sys.exit(1)

    oxipng_version = "9.1.2"
    download_url = f"https://github.com/shssoichiro/oxipng/releases/download/v{oxipng_version}/oxipng-{oxipng_version}-x86_64-unknown-linux-gnu.tar.gz"
    output_file = "oxipng.tar.gz"  # 下载的文件名
    install_dir = "/usr/local/bin"  # 安装目录

    # 下载 oxipng 文件
    download_file(download_url, output_file)

    # 创建临时解压目录
    extract_dir = "oxipng_extracted"
    os.makedirs(extract_dir, exist_ok=True)

    # 解压文件
    try:
        with tarfile.open(output_file, 'r:gz') as tar:
            tar.extractall(path=extract_dir)
    except Exception as e:
        handle_error("解压失败", e)

    # 递归查找 oxipng 可执行文件
    def find_oxipng_binary(dir_path):
        return next((os.path.join(root, 'oxipng') for root, _, files in os.walk(dir_path) if 'oxipng' in files), None)

    # 查找解压后的二进制文件
    oxipng_binary = find_oxipng_binary(extract_dir)
    if not oxipng_binary:
        print(f"\033[31m未找到 oxipng 可执行文件。\033[0m")
        sys.exit(1)

    # 移动二进制文件到 /usr/local/bin
    try:
        shutil.move(oxipng_binary, os.path.join(install_dir, "oxipng"))
        # 确保二进制文件可执行
        subprocess.run(["chmod", "+x", os.path.join(install_dir, "oxipng")], check=True)
        print(f"\033[1;32moxipng 安装成功至\033[0m {install_dir}")
    except Exception as e:
        handle_error("安装失败", e)

    # 清理临时文件和文件夹
    os.remove(output_file)
    shutil.rmtree(extract_dir)
    print("\033[33m提示:\033[0m 使用'python3 script.py unoxipng'可卸载oxipng")

    # 验证安装并输出 oxipng 版本
    try:
        subprocess.run([os.path.join(install_dir, "oxipng"), "--version"], check=True)
    except Exception as e:
        handle_error("oxipng 版本检查失败", e)

def uninstall_oxipng():
    """ 卸载 oxipng，删除 /usr/local/bin 目录下的 oxipng 可执行文件。 """
    oxipng_path = '/usr/local/bin/oxipng'
    if os.path.exists(oxipng_path):
        try:
            os.remove(oxipng_path)
            print(f"\033[1;32moxipng 已成功卸载:\033[0m {oxipng_path}")
        except Exception as e:
            handle_error("卸载失败", e)
    else:
        print("\033[31m未找到 oxipng，可执行文件未安装或已卸载。\033[0m")

def get_video_duration(video_file):
    """ 使用 ffprobe 获取视频总时长（秒）。 """
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
             "-of", "default=noprint_wrappers=1:nokey=1", video_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return float(result.stdout)
    except Exception as e:
        handle_error("无法获取视频时长", e)

def generate_random_timestamps(duration, num_screenshots):
    """生成随机截图时间戳，排除开头的5分钟和结尾的15分钟。"""
    start_time = 300  # 开头5分钟排除
    end_time = max(start_time, duration - 900)  # 结尾15分钟排除，确保范围合法

    # 生成随机时间戳
    return [f"{int(rand_time // 3600):02}:{int((rand_time % 3600) // 60):02}:{int(rand_time % 60):02}.{int((rand_time % 1) * 1000):03}"
            for rand_time in [random.uniform(start_time, end_time) for _ in range(num_screenshots)]]

def clear_directory(directory):
    """ 清空并创建目录。 """
    if (os.path.exists(directory)):
        shutil.rmtree(directory)
    os.makedirs(directory)

def get_file_size(file_path):
    return os.path.getsize(file_path) / 1024

def capture_screenshots(video_file, timestamps, output_dir):
    """ 使用 ffmpeg 截取截图。 """
    for i, timestamp in enumerate(timestamps, 1):
        output_file = os.path.join(output_dir, f"screenshot_{i:03}.png")
        result = subprocess.run(
            ["ffmpeg", "-ss", timestamp, "-i", video_file, 
             "-frames:v", "1", "-qscale:v", "0", "-vsync", "vfr", output_file],  
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode == 0:
            file_size = get_file_size(output_file)
            print(f"\033[1;32m生成无损截图:\033[0m {output_file}，\033[1;32m时间戳:\033[0m {timestamp}，\033[1;32m图片大小:\033[0m {file_size:.2f} KB")
        else:
            print(f"\033[31m生成截图失败: {result.stderr.decode().strip()}\033[0m")

def compress_image(output_file, quality):
    """ 使用 oxipng 压缩图像。 """
    compressed_file = output_file.replace('.png', f'_{quality}.png')
    print(f"\033[1;32m压缩:\033[0m {output_file}，\033[1;32m压缩级别:\033[0m {quality}")
    result = subprocess.run(
        ["oxipng", f"-o{quality}", output_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode == 0:
        os.rename(output_file, compressed_file)
        file_size = get_file_size(compressed_file)
        print(f"\033[1;32m压缩完成:\033[0m {compressed_file}，\033[1;32m压缩后大小:\033[0m {file_size:.2f} KB")
    else:
        print(f"\033[31m压缩失败: {result.stderr.decode().strip()}\033[0m")

def process_images_and_upload(output_dir):
    """将截图上传到 Pixhost，并打印出所有图片的直接链接和 BBCode"""
    url = "https://api.pixhost.to/images"
    headers = {}
    image_urls = []
    bbcode_list = []

    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as image_file:
                files = {'img': (file_name, image_file)}
                data = {'content_type': '0', 'max_th_size': '420'}
                try:
                    response = requests.post(url, data=data, files=files, headers=headers)
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'show_url' in response_data:
                            show_url = response_data['show_url']
                            # 使用正则表达式提取服务器号
                            import re
                            server_match = re.search(r"https://(?:img)?(\d+)\.pixhost\.to", show_url)
                            server_number = server_match.group(1) if server_match else "100"  # 默认为 100

                            # 构造正确的图片直接链接
                            parts = show_url.split("/")
                            direct_image_url = f"https://img{server_number}.pixhost.to/images/{parts[4]}/{parts[5]}"
                            bbcode = f"[img]{direct_image_url}[/img]"
                            image_urls.append(direct_image_url)
                            bbcode_list.append(bbcode)
                        else:
                            print(f"\033[31m图片 {file_name} 上传失败，未返回 show_url。\033[0m")
                    else:
                        print(f"\033[31m图片 {file_name} 上传失败，HTTP状态码: {response.status_code}\033[0m")
                except Exception as e:
                    print(f"\033[31m上传图片 {file_name} 时出错: {e}\033[0m")

    # 统一打印所有图片的直接链接
    if image_urls:
        print("\n\033[1;32m直接链接\033[0m:")
        for url in image_urls:
            print(url)

    # 统一打印所有图片的 BBCode
    if bbcode_list:
        print("\n\033[1;32mBBCode\033[0m:")
        for bbcode in bbcode_list:
            print(bbcode)

def process_compression(output_dir, num_screenshots, quality, max_workers=None):
    """ 批量压缩截图，支持多线程。 """
    if max_workers is None or max_workers > 1:
        print("模式：多线程")
    else:
        print("模式：单线程")

    def compress_file(i):
        output_file = os.path.join(output_dir, f"screenshot_{i:03}.png")
        compress_image(output_file, quality)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(compress_file, range(1, num_screenshots + 1))

def determine_compression_quality():
    """ 获取压缩质量，优先从命令行参数获取，否则从用户输入获取 """
    if len(sys.argv) > 3 and sys.argv[3].isdigit():
        return int(sys.argv[3])
    elif '-t' in sys.argv:
        return get_compression_quality()
    return None

def get_compression_quality():
    """ 获取用户输入的压缩质量。 """
    try:
        quality = int(input("请输入压缩质量 (1-6): "))
        if 1 <= quality <= 6:
            return quality
        else:
            print("\033[31m无效的压缩质量值，必须在 1-6 之间。\033[0m")
            sys.exit(1)
    except ValueError:
        print("\033[31m输入的不是有效的数字。\033[0m")
        sys.exit(1)

def main():
    """ 主函数，处理命令行参数并执行操作。 """
    if len(sys.argv) < 2:
        print("\033[31m错误: 缺少参数。用法: python3 script.py 视频文件 截图数量 (压缩质量) (-t)\033[0m")
        sys.exit(1)

    if sys.argv[1] == 'oxipng':
        print("开始安装 oxipng...")
        install_oxipng()
        sys.exit(0)
    elif sys.argv[1] == 'unoxipng':
        print("开始卸载 oxipng...")
        uninstall_oxipng()
        sys.exit(0)

    if len(sys.argv) < 3 or (sys.argv[2] == '-t' and len(sys.argv) < 4):
        print("\033[31m错误: 缺少截图数量参数。用法: python3 script.py 视频文件 截图数量 (压缩质量) (-t)\033[0m")
        sys.exit(1)

    video_file = sys.argv[1]
    try:
        num_screenshots = int(sys.argv[2]) if sys.argv[2] != '-t' else int(sys.argv[3])
    except (ValueError, IndexError):
        print("\033[31m错误: 截图数量必须为有效的整数。用法: python3 script.py 视频文件 截图数量 (压缩质量) (-t)\033[0m")
        sys.exit(1)

    if num_screenshots < 1:
        print("\033[31m错误: 截图数量必须大于或等于1。\033[0m")
        sys.exit(1)

    if num_screenshots > 50:
        user_input = input(f"\033[33m警告: 截图数量为 {num_screenshots}，数量较多。是否继续？(y/N): \033[0m").strip().lower()
        if user_input != 'y':
            print("\033[31m操作已取消。\033[0m")
            sys.exit(1)

    max_workers = 1 if '-t' in sys.argv else None

    # 检查 ffmpeg 是否安装，ffmpeg 必须存在，否则退出
    if not check_program_installed('ffmpeg'):
        print("\033[31m错误: 未安装 ffmpeg，请先安装后再运行脚本。\033[0m")
        sys.exit(1)

    # 检查 oxipng 是否安装，oxipng 是可选的
    oxipng_installed = check_program_installed('oxipng')
    
    if not oxipng_installed:
        print("\033[33m提示:\033[0m 未安装 oxipng，所有压缩功能不可用。")
        print("\033[33m提示:\033[0m 如需压缩请使用'python3 script.py oxipng'安装oxipng(仅amd)")

    output_dir = "screenshots"
    clear_directory(output_dir)

    # 生成截图
    duration = get_video_duration(video_file)
    timestamps = generate_random_timestamps(duration, num_screenshots)
    capture_screenshots(video_file, timestamps, output_dir)

    # 判断压缩逻辑
    if oxipng_installed:
        quality = None
        if len(sys.argv) == 3 and max_workers is None:
            # 用法 (1): 询问用户是否需要压缩
            compress = input("是否需要压缩图片？回车默认不压缩(y/N): ").strip().lower()
            if compress == 'y':
                quality = get_compression_quality()
        elif len(sys.argv) > 3 and sys.argv[3].isdigit():
            # 用法 (2) 和 (3): 用户直接传入了压缩质量，自动压缩
            try:
                quality = int(sys.argv[3])
            except ValueError:
                print("\033[31m错误: 压缩质量必须为 1 到 6 的整数。\033[0m")
                sys.exit(1)
        elif '-t' in sys.argv and len(sys.argv) == 4:
            # 用法 (4): 需要压缩但未传入质量，询问压缩质量
            quality = get_compression_quality()

        # 处理压缩
        if quality:
            process_compression(output_dir, num_screenshots, quality, max_workers)

    # 上传截图到 Pixhost
    process_images_and_upload(output_dir)

if __name__ == "__main__":
    main()
