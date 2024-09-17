from pathlib import Path
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
    def __init__(self, text_widget, level=logging.INFO):
        super().__init__()
        self.text_widget = text_widget
        self.setLevel(level)
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        # 为不同日志级别配置标签
        self.text_widget.tag_config("INFO", foreground="green")
        self.text_widget.tag_config("ERROR", foreground="red")
        self.text_widget.tag_config("WARNING", foreground="orange")
        self.text_widget.tag_config("DEBUG", foreground="blue")

    def emit(self, record):
        # 格式化消息
        msg = self.format(record)
        # 根据日志级别插入不同颜色的文本
        if record.levelno == logging.INFO:
            tag = "INFO"
        elif record.levelno == logging.ERROR:
            tag = "ERROR"
        elif record.levelno == logging.WARNING:
            tag = "WARNING"
        elif record.levelno == logging.DEBUG:
            tag = "DEBUG"
        else:
            tag = None

        # 在 Text 小部件中插入消息，并根据级别应用标签
        self.text_widget.insert(tk.END, msg + '\n', tag)
        self.text_widget.see(tk.END)


LOGGER = get_logger(__name__)
