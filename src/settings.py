from pathlib import Path
import queue
import tkinter as tk
import logging

ROOT = Path(__file__).parents[1]


def get_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 控制台输出   
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s,%(lineno)d] - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


class TextHandler(logging.Handler):
    def __init__(self, root: tk.Tk, text_widget: tk.Text, log_queue: queue.Queue, level=logging.INFO):
        super().__init__()
        self.root = root
        self.text_widget = text_widget
        self.log_queue = log_queue
        self.setLevel(level)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 为不同日志级别配置标签
        self.text_widget.tag_config("INFO", foreground="green")
        self.text_widget.tag_config("ERROR", foreground="red")
        self.text_widget.tag_config("WARNING", foreground="orange")
        self.text_widget.tag_config("DEBUG", foreground="blue")

    def emit(self, record):
        # 格式化消息并将其放入队列
        msg = self.format(record)
        self.log_queue.put((msg, record.levelno))

    def process_queue(self):
        # 从队列中读取日志并插入到 Text 小部件中
        try:
            while True:
                msg, levelno = self.log_queue.get_nowait()  # 不阻塞地获取日志
                # 根据日志级别选择标签
                if levelno == logging.INFO:
                    tag = "INFO"
                elif levelno == logging.ERROR:
                    tag = "ERROR"
                elif levelno == logging.WARNING:
                    tag = "WARNING"
                elif levelno == logging.DEBUG:
                    tag = "DEBUG"
                else:
                    tag = None

                # 在 Text 小部件中插入消息，并根据级别应用标签
                self.text_widget.insert(tk.END, msg + '\n', tag)
                self.text_widget.see(tk.END)
        except queue.Empty:
            pass

        # 继续定期检查队列
        self.root.after(100, self.process_queue)


LOGGER = get_logger(__name__, logging.DEBUG)
