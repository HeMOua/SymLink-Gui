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
        LOGGER.debug(f"Moved file: \"{source_path.resolve()}\" to \"{dest_path.resolve()}\"")
    
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
    LOGGER.debug(f"Removed empty folder: \"{source_folder.resolve()}\"")


def make_symlink(_src: str, _dst: str, preview):
    if preview:
        LOGGER.info("Preview Mode".center(40, "="))
        LOGGER.info("Currently in preview mode, it will not have any impact on the directory.")
    else:
        LOGGER.info("Execution Mode".center(40, "="))
    LOGGER.info(f"Start creating symlink from {_src} to {_dst}.")
    t0 = time.time()
    
    try:
        # 检查值
        if not _src and not _dst:
            raise ValueError("Source and target folders are empty.")
        elif not _src:
            raise ValueError("Source folder is empty.")
        elif not _dst:
            raise ValueError("Target folder is empty.")
        
        src = Path(_src)
        dst = Path(_dst)

        # 检查路径
        if not src.exists():
            raise FileNotFoundError(f"Source path \"{src}\" does not exist.")
        if dst.exists():
            raise FileExistsError(f"Destination path \"{dst}\" already exists.")
        if str(dst).startswith(str(src)):
            raise ValueError(f"Destination path \"{dst}\" is a subdirectory of source path \"{src}\".")

        # 移动文件
        move_all(src, dst, preview)

        # 创建软链接
        if not preview:
            os.symlink(dst, src)
        
        LOGGER.info(f"Finished creating symlink from \"{src}\" to \"{dst}\".")
    except Exception as e:
        LOGGER.error(f"Failed to create symlink from \"{src}\" to \"{dst}\".")
        LOGGER.error(e)
        return
    finally:
        LOGGER.info(f"Time elapsed: {time.time() - t0:.2f}s")

        if preview:
            LOGGER.info("Preview Mode End".center(40, "=") + "\n")
        else:
            LOGGER.info("Execution Mode End".center(40, "=") + "\n")
