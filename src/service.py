import os
import time
from pathlib import Path
from settings import LOGGER
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed


def is_folder_empty(folder: Path) -> bool:
    """递归检查文件夹及其子文件夹是否为空"""
    for item in folder.iterdir():
        if item.is_dir():
            if not is_folder_empty(item):
                return False
        else:
            return False
    return True


def move(src, dst, preview):
    # 获取源文件和目标文件所在的磁盘
    src_drive = os.path.splitdrive(src)[0]
    dst_drive = os.path.splitdrive(dst)[0]

    try:
        # 如果在同一磁盘上，使用 os.rename
        if src_drive == dst_drive:
            if not preview:
                os.rename(src, dst)
            opt_type = 'RENAME'
        else:
            # 如果不在同一磁盘上，使用 shutil.move
            if not preview:
                shutil.move(src, dst)
            opt_type = 'MOVE'
        LOGGER.debug(f"移动文件[{opt_type}]: \"{src}\" 到 \"{dst}\"")
    except Exception as e:
        LOGGER.error(f"移动文件失败：{e}")
        raise e


def move_file_or_folder(source_path: Path, dest_folder: Path, preview):
    # 如果是文件，直接移动
    if source_path.is_file():
        if not preview:
            dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / source_path.name

        move(source_path, dest_path, preview)
    
    # 如果是文件夹
    elif source_path.is_dir():
        if is_folder_empty(source_path):
            # 如果文件夹为空或没有任何子文件，直接移动整个目录
            dest_path = dest_folder / source_path.name
            if not preview:
                shutil.move(str(source_path), str(dest_path))
            LOGGER.debug(f"直接移动文件夹 \"{source_path}\" 到 \"{dest_path}\"")
        else:
            # 否则递归移动其中的内容
            new_dest_folder = dest_folder / source_path.name
            move_all(source_path, new_dest_folder, preview)
        

# 定义递归移动所有文件和文件夹的函数
def move_all(source_folder: Path, dest_folder: Path, preview):
    # 获取文件夹中的所有项目（文件和文件夹）
    items = list(source_folder.iterdir())

    # 如果项目数量为 0 或 1，不需要使用多线程
    if len(items) == 0:
        LOGGER.debug(f"源文件夹 \"{source_folder}\" 为空，无需移动。")
    elif len(items) == 1:
        # 如果只有一个项目，直接移动即可
        move_file_or_folder(items[0], dest_folder, preview)
    else:
        # 使用多线程移动文件或文件夹
        max_workers = min(8, len(items))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(move_file_or_folder, item, dest_folder, preview) for item in items]

            # 确保所有任务完成并记录异常
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    LOGGER.error("移动项目时出错: %s", e, exc_info=True)
    
    # 删除空的源文件夹
    if not preview:
        try:
            if is_folder_empty(source_folder):
                shutil.rmtree(source_folder)
                LOGGER.debug(f"删除空文件夹: \"{source_folder}\"")
            else:
                LOGGER.warning(f"未删除文件夹 {source_folder}，因为它不是空的。")
        except Exception as e:
            LOGGER.error(f"删除文件夹 {source_folder} 时出错: {e}")


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
        
        src = Path(_src).resolve()
        dst = Path(_dst).resolve()

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
            os.symlink(dst, src, target_is_directory=True)
        
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
