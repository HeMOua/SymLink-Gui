import sys
import logging
import queue
import os
import threading
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from settings import ROOT, LOGGER, TextHandler
from tkinterdnd2 import TkinterDnD, DND_FILES
from pathlib import Path
from service import make_symlink


if getattr(sys, 'frozen', None):
    basedir = sys._MEIPASS
else:
    basedir = str(Path(__file__).parents[1].resolve())


class MainWindow(TkinterDnD.Tk):
    def __init__(self, title="Main Window", width=400, height=200):
        super().__init__()
        self._title = title
        self._width = width
        self._height = height

        self.init_window()
        self.init_view()
        self.init_event()
        self.init_logging()

    def init_logging(self):
        self.log_queue = queue.Queue()
        self.text_handler = TextHandler(self, self.tab1_txt, self.log_queue, level=logging.DEBUG)
        LOGGER.addHandler(self.text_handler)
        self.after(100, self.process_queue)

    def init_window(self):
        # 标题
        self.title(self._title)

        # 图标
        self.iconbitmap(os.path.join(basedir, "symlink.ico"))

        # 获取屏幕的宽度和高度
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算窗口在屏幕中央的位置
        position_x = (screen_width // 2) - (self._width // 2)
        position_y = (screen_height // 2) - (self._height // 2)
        self.geometry(f"{self._width}x{self._height}+{position_x}+{position_y}")

        # 禁止调整窗口大小
        # self.resizable(True, False)

    def init_view(self):

        def on_checkbox_changed(var, entry):
            entry.config(state='normal' if var.get() == 1 else 'disabled')

        def on_button_click(var):
            folder_selected = filedialog.askdirectory()
            var.set(folder_selected)

        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[4, 4], font=('微软雅黑', 10))
        style.layout("Tab", [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
                    ('Notebook.label', {'side': 'top', 'sticky': ''})],
            })],
        })])

        notebook = ttk.Notebook(self)

        # 选项卡1
        tab1 = ttk.Frame(notebook)
        # Frame1 Start
        frame1 = ttk.LabelFrame(tab1, text="源文件夹选择")
        # row1 label
        tab1_lab1 = ttk.Label(frame1, text="源文件夹:", width=9, anchor="e")
        tab1_lab1.grid(row=0, column=0, padx=10, pady=10)
        # row1 entry
        tab1_ent1_src_var = tk.StringVar()
        tab1_ent1_src_pth = ttk.Entry(frame1, textvariable=tab1_ent1_src_var, takefocus=False)
        tab1_ent1_src_pth.drop_target_register(DND_FILES)
        tab1_ent1_src_pth.config(state='readonly')
        tab1_ent1_src_pth.grid(row=0, column=1, sticky='ew')
        self.tab1_ent1_src_pth = tab1_ent1_src_pth
        self.tab1_ent1_src_var = tab1_ent1_src_var
        # row1 button
        tab1_sel_src = ttk.Button(frame1, text="选择", takefocus=False)
        tab1_sel_src.grid(row=0, column=2, padx=10, pady=10)
        self.tab1_sel_src = tab1_sel_src
        # row2 checkbutton
        src_check_var = tk.IntVar(value=0)
        tab1_check_src_enb = tk.Checkbutton(frame1, text=":", variable=src_check_var, takefocus=False)
        tab1_check_src_enb.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='e')
        # row2 entry
        tab1_ent2_src_tpth_var = tk.StringVar()
        tab1_ent2_src_tpth = ttk.Entry(frame1, textvariable=tab1_ent2_src_tpth_var, takefocus=False, state='disabled')
        tab1_ent2_src_tpth.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=(0, 10), sticky='ew')
        src_check_var.trace_add('write', lambda *args: on_checkbox_changed(src_check_var, tab1_ent2_src_tpth))
        tab1_sel_src.config(command=lambda: on_button_click(tab1_ent1_src_var))
        self.tab1_ent2_src_tpth = tab1_ent2_src_tpth
        self.tab1_ent2_src_tpth_var = tab1_ent2_src_tpth_var
        # config frame1
        frame1.columnconfigure(1, weight=1)
        frame1.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        # Frame1 End
        
        # Frame2 Start
        frame2 = ttk.LabelFrame(tab1, text="目标文件夹选择")
        # row1 label
        tab1_lab2 = ttk.Label(frame2, text="目标文件夹:", width=9, anchor="e")
        tab1_lab2.grid(row=0, column=0, padx=10, pady=10)
        # row1 entry
        tab1_ent2_tar_var = tk.StringVar()
        tab1_ent2_tar_pth = ttk.Entry(frame2, textvariable=tab1_ent2_tar_var, takefocus=False)
        tab1_ent2_tar_pth.drop_target_register(DND_FILES)
        tab1_ent2_tar_pth.config(state='readonly')
        tab1_ent2_tar_pth.grid(row=0, column=1, sticky='ew')
        self.tab1_ent2_tar_pth = tab1_ent2_tar_pth
        self.tab1_ent2_tar_var = tab1_ent2_tar_var
        # row1 button
        tab1_sel_tar = ttk.Button(frame2, text="选择", takefocus=False)
        tab1_sel_tar.grid(row=0, column=2, padx=10, pady=10)
        self.tab1_sel_tar = tab1_sel_tar
        # row2 checkbutton
        tar_check_var = tk.IntVar(value=0)
        tab1_check_tar_enb = tk.Checkbutton(frame2, text=":", variable=tar_check_var, takefocus=False)
        tab1_check_tar_enb.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='e')
        # row2 entry
        tab1_ent2_tar_tpth_var = tk.StringVar()
        tab1_ent2_tar_tpth = ttk.Entry(frame2, textvariable=tab1_ent2_tar_tpth_var, takefocus=False, state='disabled')
        tab1_ent2_tar_tpth.grid(row=1, column=1, columnspan=2, padx=(0, 10), pady=(0, 10), sticky='we')
        tar_check_var.trace_add('write', lambda *args: on_checkbox_changed(tar_check_var, tab1_ent2_tar_tpth))
        tab1_sel_tar.config(command=lambda: on_button_click(tab1_ent2_tar_var))
        self.tab1_ent2_tar_tpth = tab1_ent2_tar_tpth
        self.tab1_ent2_tar_tpth_var = tab1_ent2_tar_tpth_var
        # config frame2
        frame2.columnconfigure(1, weight=1)
        frame2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='ew')
        # Frame2 End

        # Textbox Start
        text_frame = ttk.Frame(tab1)

        tab1_txt = tk.Text(text_frame, wrap='word')
        tab1_txt.pack(expand=True, fill='both')

        text_scroll = tk.Scrollbar(text_frame, orient='vertical', command=tab1_txt.yview)
        text_scroll.pack(side='right', fill='y')
        tab1_txt.config(yscrollcommand=text_scroll.set)
        text_scroll.config(command=tab1_txt.yview)

        text_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.tab1_txt = tab1_txt
        # Textbox End

        # Frame3 Start
        frame4 = ttk.Frame(tab1)
        enable_debug_check_var = tk.IntVar(value=0)
        enable_debug_check = tk.Checkbutton(frame4, text="调试模式", variable=enable_debug_check_var, takefocus=False)
        enable_debug_check.grid(row=0, column=0, padx=(0, 5))
        self.enable_debug_check_var = enable_debug_check_var
        tab1_prev = ttk.Button(frame4, text="预览", takefocus=False, command=lambda: self.exec(preview=True))
        tab1_prev.grid(row=0, column=1, padx=(0, 5), sticky='ew')
        self.tab1_prev = tab1_prev
        tab1_exec = ttk.Button(frame4, text="执行", takefocus=False, command=lambda: self.exec())
        tab1_exec.grid(row=0, column=2, padx=(5, 0), sticky='ew')
        self.tab1_exec = tab1_exec
        tab1_clear = ttk.Button(frame4, text="清空", takefocus=False, command=lambda: self.tab1_txt.delete(1.0, tk.END))
        tab1_clear.grid(row=0, column=3, padx=(5, 0), sticky='ew')
        frame4.columnconfigure(1, weight=1)
        frame4.columnconfigure(2, weight=1)
        frame4.columnconfigure(3, weight=1)
        frame4.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
        # Frame3 End

        tab1.columnconfigure(0, weight=1)
        tab1.rowconfigure(2, weight=1)
        tab1.pack(expand=True, fill='both')
        notebook.add(tab1, text='自动模式')

        # 选项卡2
        tab2 = ttk.Frame(notebook)
        notebook.add(tab2, text='手动模式')

        notebook.pack(expand=True, fill='both', padx=8, pady=8)

    def init_event(self):

        def on_drag_enter(e, var):
            path = e.data
            if path:
                if os.path.isdir(path):
                    var.set(path)
                else:
                    LOGGER.warning(f"\"{path}\" 不是文件夹。")

        def on_change_src():
            src_folder_name = os.path.basename(self.tab1_ent1_src_var.get())
            tar_folder_name = os.path.basename(self.tab1_ent2_tar_var.get())
            self.tab1_ent2_src_tpth_var.set(self.tab1_ent1_src_var.get())
            if tar_folder_name == '': return
            elif src_folder_name != tar_folder_name:
                path = Path(self.tab1_ent2_tar_var.get()) / src_folder_name
                self.tab1_ent2_tar_tpth_var.set(path.resolve().as_posix())

        def on_change_tar():
            src_path = self.tab1_ent1_src_var.get()
            tar_path = self.tab1_ent2_tar_var.get()
            if src_path:
                folder_name = os.path.basename(src_path)
                path = Path(tar_path) / folder_name
                self.tab1_ent2_tar_tpth_var.set(path.resolve().as_posix())
            else:
                self.tab1_ent2_tar_tpth_var.set(tar_path)

        self.tab1_ent1_src_pth.dnd_bind('<<Drop>>', lambda e: on_drag_enter(e, self.tab1_ent1_src_var))
        self.tab1_ent2_tar_pth.dnd_bind('<<Drop>>', lambda e: on_drag_enter(e, self.tab1_ent2_tar_var))

        self.tab1_ent1_src_var.trace_add('write', lambda *args: on_change_src())
        self.tab1_ent2_tar_var.trace_add('write', lambda *args: on_change_tar())
        
    def process_queue(self):
        last_tag = None
        logs_buffer = ""

        # 从队列中读取日志并插入到 Text 小部件中
        while not self.log_queue.empty():
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

            # 如果 tag 发生变化或没有初始化
            if tag != last_tag and logs_buffer:
                # 先将之前相同 tag 的日志插入
                self.tab1_txt.insert(tk.END, logs_buffer, last_tag)
                self.tab1_txt.see(tk.END)
                logs_buffer = ""  # 清空缓冲区
                last_tag = tag  # 更新 last_tag

            # 拼接相同 tag 的日志
            logs_buffer += msg + '\n'

        # 插入剩余的日志
        if logs_buffer:
            self.tab1_txt.insert(tk.END, logs_buffer, last_tag)
            self.tab1_txt.see(tk.END)

        # 继续定期检查队列
        self.after(100, self.process_queue)

    def make_make_symlink_in_thread(self, src, dst, preview):
        threading.Thread(target=make_symlink, args=(src, dst, preview)).start()

    def exec(self, preview=False):
        self.text_handler.setLevel(logging.DEBUG if self.enable_debug_check_var.get() == 1 else logging.INFO)

        src = self.tab1_ent2_src_tpth_var.get()
        dst = self.tab1_ent2_tar_tpth_var.get()

        self.make_make_symlink_in_thread(src, dst, preview)

    def run(self):
        self.mainloop()        


if __name__ == '__main__':
    app = MainWindow('软链接 SymLink - By HeMOu', 600, 500)
    app.run()