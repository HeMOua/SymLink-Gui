import os
import time
from pathlib import Path
from settings import LOGGER
import shutil
from concurrent.futures import ThreadPoolExecutor


# 定义文件移动的函数
def move_file_or_folder(source_path: Path, dest_folder: Path, preview):
    # 如果是文件，直接移动
    if source_path.is_file():
        if not preview:
            dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / source_path.name

        if not preview:
            shutil.move(str(source_path), str(dest_path))
        LOGGER.debug(f"移动文件: \"{source_path.resolve()}\" 到 \"{dest_path.resolve()}\"")
    
    # 如果是文件夹，递归移动其中的内容
    elif source_path.is_dir():
        new_dest_folder = dest_folder / source_path.name
        move_all(source_path, new_dest_folder, preview)
        

# 定义递归移动所有文件和文件夹的函数
def move_all(source_folder: Path, dest_folder: Path, preview):
    # 获取文件夹中的所有项目（文件和文件夹）
    items = list(source_folder.iterdir())

    # 使用多线程移动文件或文件夹
    with ThreadPoolExecutor() as executor:
        for item in items:
            executor.submit(move_file_or_folder, item, dest_folder, preview)
    
    # 删除空的源文件夹
    if not preview:
        shutil.rmtree(source_folder)
    LOGGER.debug(f"删除空文件夹: \"{source_folder.resolve()}\"")


def make_symlink(_src: str, _dst: str, preview):
    if preview:
        LOGGER.info("预览模式".center(40, "="))
        LOGGER.info("预览模式下不会创建软链接，只会显示模拟移动和删除的操作。")
    else:
        LOGGER.info("执行模式".center(40, "="))

    LOGGER.info(f"开始创建软链接，源路径：{_src}，目标路径：{_dst}。")
    t0 = time.time()
    
    try:
        # 检查值
        if not _src and not _dst:
            raise ValueError("源路径和目标路径均为空。")
        elif not _src:
            raise ValueError("源路径为空。")
        elif not _dst:
            raise ValueError("目标路径为空。")
        
        src = Path(_src)
        dst = Path(_dst)

        # 检查路径
        if not src.exists():
            raise FileNotFoundError(f"源路径 \"{src}\" 不存在。")
        if dst.exists():
            raise FileExistsError(f"目标路径 \"{dst}\" 已存在。")
        if str(dst).startswith(str(src)):
            raise ValueError(f"目标路径 \"{dst}\" 不能是源路径 \"{src}\" 的子目录。")

        # 移动文件
        move_all(src, dst, preview)

        # 创建软链接
        if not preview:
            os.symlink(dst, src)
        
        LOGGER.info(f"创建软链接成功，源路径：{_src}，目标路径：{_dst}。")
    except Exception as e:
        LOGGER.error(f"创建软链接失败：{e}")
        LOGGER.error(e)
        return
    finally:
        LOGGER.info(f"耗时: {time.time() - t0:.2f}s")

        if preview:
            LOGGER.info("预览模式结束".center(40, "=") + "\n")
        else:
            LOGGER.info("执行模式结束".center(40, "=") + "\n")
