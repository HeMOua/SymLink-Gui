import logging
import queue
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from settings import ROOT, LOGGER, TextHandler
from tkinterdnd2 import TkinterDnD, DND_FILES
from pathlib import Path
from service import make_symlink



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
        log_queue = queue.Queue()
        self.text_handler = TextHandler(self, self.tab1_txt, log_queue, level=logging.DEBUG)
        LOGGER.addHandler(self.text_handler)
        self.after(100, self.text_handler.process_queue)

    def init_window(self):
        # 标题
        self.title(self._title)

        # 图标
        self.iconbitmap(ROOT / 'assets/symlink.ico')

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
        # notebook = ttk.Notebook(self)

        # style = ttk.Style()
        # style.configure('TNotebook.Tab', padding=[10, 5], font=('宋体', 10))
        # style.layout("Tab", [
        #     ('Notebook.tab', {'sticky': 'nswe', 'children': [
        #         ('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children': [
        #             ('Notebook.label', {'side': 'top', 'sticky': ''})],
        #     })],
        # })])

        def on_checkbox_changed(var, entry):
            entry.config(state='normal' if var.get() == 1 else 'disabled')

        def on_button_click(var):
            folder_selected = filedialog.askdirectory()
            var.set(folder_selected)

        # 选项卡1
        tab1 = ttk.Frame(self)
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
        tab1_txt = tk.Text(tab1)
        tab1_txt.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        tab1_txt.tag_config('info', foreground='blue')
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
        frame4.columnconfigure(1, weight=1)
        frame4.columnconfigure(2, weight=1)
        frame4.grid(row=3, column=0, padx=10, pady=(0, 10), sticky='ew')
        # Frame3 End

        # notebook.add(tab1, text='文件模式')
        tab1.columnconfigure(0, weight=1)
        tab1.rowconfigure(2, weight=1)
        tab1.pack(expand=True, fill='both')

    def init_event(self):

        def on_drag_enter(e, var):
            path = e.data
            if path:
                if os.path.isdir(path):
                    var.set(path)
                else:
                    LOGGER.warning(f"\"{path}\" is not a directory.")

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
        
    def exec(self, preview=False):
        self.text_handler.setLevel(logging.DEBUG if self.enable_debug_check_var.get() == 1 else logging.INFO)

        src = self.tab1_ent2_src_tpth_var.get()
        dst = self.tab1_ent2_tar_tpth_var.get()

        make_symlink(src, dst, preview)

    def run(self):
        self.mainloop()        
