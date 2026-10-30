"""RISC-16 Simulator GUI - Pembe Tema"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.cpu import CPU
from src.assembler.encoder import Assembler
from src.utils.helpers import format_hex, format_binary, disassemble


class PinkTheme:
    BG = "#FFF0F5"
    BG_DARK = "#FFE4EC"
    PRIMARY = "#FF69B4"
    SECONDARY = "#FFB6C1"
    ACCENT = "#FF1493"
    WHITE = "#FFFFFF"
    TEXT = "#333333"
    TEXT_LIGHT = "#888888"
    
    # Pipeline
    FETCH = "#FF69B4"
    DECODE = "#FF85A2"
    EXECUTE = "#DB7093"
    MEMORY = "#C71585"
    WRITEBACK = "#8B008B"
    
    # Hazard
    STALL = "#DC3545"
    FLUSH = "#FD7E14"
    FORWARD = "#28A745"
    NORMAL = "#6C757D"


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌸 RISC-16 Processor Simulator")
        self.root.geometry("1450x820")
        self.root.configure(bg=PinkTheme.BG)
        
        self.cpu = CPU()
        self.assembler = Assembler()
        self.running = False
        self.step_delay = 100
        self.prev_regs = [0] * 8
        
        self._create_menu()
        self._create_layout()
        self._update_display()
    
    def _create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="📁 Dosya", menu=file_menu)
        file_menu.add_command(label="Aç...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Kaydet", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)
        
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="▶ Çalıştır", menu=run_menu)
        run_menu.add_command(label="Assemble (F5)", command=self._assemble)
        run_menu.add_command(label="Geri (F6)", command=self._step_back)
        run_menu.add_command(label="Adım (F7)", command=self._step)
        run_menu.add_command(label="Çalıştır (F9)", command=self._run)
        run_menu.add_command(label="Durdur", command=self._stop)
        run_menu.add_command(label="Reset (F2)", command=self._reset)
        
        self.root.bind('<Control-o>', lambda e: self._open_file())
        self.root.bind('<Control-s>', lambda e: self._save_file())
        self.root.bind('<F5>', lambda e: self._assemble())
        self.root.bind('<F6>', lambda e: self._step_back())
        self.root.bind('<F7>', lambda e: self._step())
        self.root.bind('<F9>', lambda e: self._run())
        self.root.bind('<F2>', lambda e: self._reset())
    
    def _create_layout(self):
        # Ana container
        main = tk.Frame(self.root, bg=PinkTheme.BG)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Üst kısım
        top = tk.Frame(main, bg=PinkTheme.BG)
        top.pack(fill=tk.BOTH, expand=True)
        
        # Sol - Assembly Kodu
        self._create_code_panel(top)
        
        # Orta - Pipeline
        self._create_pipeline_panel(top)
        
        # Sağ - Registers
        self._create_register_panel(top)
        
        # Alt kısım
        bottom = tk.Frame(main, bg=PinkTheme.BG)
        bottom.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self._create_machine_code_panel(bottom)
        self._create_imem_panel(bottom)
        self._create_dmem_panel(bottom)
        
        # Status bar
        self._create_status_bar()
    
    def _create_panel(self, parent, title, width=None):
        frame = tk.Frame(parent, bg=PinkTheme.BG_DARK, relief=tk.RIDGE, bd=2)
        if width:
            frame.configure(width=width)
        
        header = tk.Label(frame, text=title, font=('Arial', 11, 'bold'),
                         bg=PinkTheme.BG_DARK, fg=PinkTheme.PRIMARY)
        header.pack(anchor='w', padx=10, pady=(8, 5))
        
        return frame
    
    def _create_code_panel(self, parent):
        frame = self._create_panel(parent, "💻 Assembly Kodu")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Editor
        editor_border = tk.Frame(frame, bg=PinkTheme.PRIMARY, bd=2)
        editor_border.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.code_editor = scrolledtext.ScrolledText(
            editor_border, width=45, height=18,
            font=('Consolas', 11), bg=PinkTheme.WHITE, fg=PinkTheme.TEXT,
            insertbackground=PinkTheme.PRIMARY, relief=tk.FLAT, bd=5
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        self.code_editor.insert('1.0', self._default_program())
        
        # Butonlar
        btn_frame = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("⚡ Assemble (F5)", self._assemble, "#FF69B4"),   # Hot pink
            ("◀ Geri (F6)", self._step_back, "#FF8C00"),       # Orange - YENİ
            ("👣 Adım (F7)", self._step, "#9370DB"),           # Purple
            ("🚀 Çalıştır (F9)", self._run, "#32CD32"),        # Green
            ("⏹ Durdur", self._stop, "#FF6347"),              # Red
            ("🔄 Reset (F2)", self._reset, "#4169E1"),         # Blue
        ]
        
        for text, cmd, color in buttons:
            # Frame ile özel buton (macOS için)
            btn_container = tk.Frame(btn_frame, bg=color, bd=0, relief=tk.RAISED)
            btn_container.pack(side=tk.LEFT, padx=3)
            
            btn = tk.Label(btn_container, text=text, bg=color, fg='white',
                          font=('Arial', 10, 'bold'), padx=12, pady=8, cursor='hand2')
            btn.pack()
            
            # Click event
            btn.bind('<Button-1>', lambda e, c=cmd: c())
            # Hover efekti
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#333333'))
            btn.bind('<Leave>', lambda e, b=btn, c=color: b.config(bg=c))
        
        # Hız kontrolü
        speed_frame = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        speed_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        tk.Label(speed_frame, text="⏱ Clock Rate Control", font=('Arial', 10, 'bold'),
                bg=PinkTheme.BG_DARK, fg=PinkTheme.PRIMARY).pack(anchor='w')
        
        slider_row = tk.Frame(speed_frame, bg=PinkTheme.BG_DARK)
        slider_row.pack(fill=tk.X, pady=5)
        
        tk.Label(slider_row, text="🐢 Yavaş", bg=PinkTheme.BG_DARK,
                fg=PinkTheme.TEXT, font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=100)
        self.speed_scale = tk.Scale(slider_row, from_=500, to=20, orient=tk.HORIZONTAL,
                                    variable=self.speed_var, command=self._update_speed,
                                    bg=PinkTheme.BG_DARK, fg=PinkTheme.TEXT,
                                    highlightthickness=0, troughcolor=PinkTheme.SECONDARY,
                                    activebackground=PinkTheme.PRIMARY, length=150,
                                    showvalue=False)
        self.speed_scale.pack(side=tk.LEFT, padx=10)
        
        tk.Label(slider_row, text="🐇 Hızlı", bg=PinkTheme.BG_DARK,
                fg=PinkTheme.TEXT, font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.speed_label = tk.Label(slider_row, text="100 ms", font=('Consolas', 10, 'bold'),
                                   bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT, padx=10, pady=2)
        self.speed_label.pack(side=tk.LEFT, padx=(15, 5))
        
        self.hz_label = tk.Label(slider_row, text="(10.0 Hz)", font=('Consolas', 9),
                                bg=PinkTheme.BG_DARK, fg=PinkTheme.TEXT_LIGHT)
        self.hz_label.pack(side=tk.LEFT)
    
    def _create_pipeline_panel(self, parent):
        frame = self._create_panel(parent, "⚡ Pipeline Stages")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        stages_frame = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        stages_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.pipeline_labels = {}
        self.pipeline_frames = {}
        
        stages = [
            ('🔵 Fetch', 'IF', PinkTheme.FETCH),
            ('🔍 Decode', 'ID', PinkTheme.DECODE),
            ('⚙ Execute', 'EX', PinkTheme.EXECUTE),
            ('📦 Memory', 'MEM', PinkTheme.MEMORY),
            ('✏ WriteBack', 'WB', PinkTheme.WRITEBACK),
        ]
        
        for icon, stage, color in stages:
            row = tk.Frame(stages_frame, bg=PinkTheme.BG_DARK)
            row.pack(fill=tk.X, pady=4)
            
            # Renkli çizgi
            bar = tk.Frame(row, bg=color, width=5)
            bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))
            
            # Stage ismi
            tk.Label(row, text=icon, font=('Arial', 10, 'bold'), width=12,
                    bg=PinkTheme.BG_DARK, fg=color, anchor='w').pack(side=tk.LEFT)
            
            # Instruction
            lbl = tk.Label(row, text="---", font=('Consolas', 10), width=28,
                          bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT, anchor='w',
                          padx=10, pady=6)
            lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            self.pipeline_labels[stage] = lbl
        
        # Hazard göstergesi
        hazard_container = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        hazard_container.pack(fill=tk.X, padx=10, pady=(10, 15))
        
        tk.Label(hazard_container, text="⚠ Hazards:", font=('Arial', 10, 'bold'),
                bg=PinkTheme.BG_DARK, fg=PinkTheme.PRIMARY).pack(side=tk.LEFT)
        
        self.hazard_frame = tk.Frame(hazard_container, bg=PinkTheme.SECONDARY)
        self.hazard_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        self.hazard_label = tk.Label(self.hazard_frame, text="✅ None", 
                                    font=('Arial', 10, 'bold'),
                                    bg=PinkTheme.SECONDARY, fg=PinkTheme.FORWARD,
                                    padx=15, pady=6)
        self.hazard_label.pack(fill=tk.X)
    
    def _create_register_panel(self, parent):
        frame = self._create_panel(parent, "📊 Registers")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(5, 0))
        
        reg_container = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        reg_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.reg_labels = {}
        self.reg_frames = {}
        
        names = ['R0 (zero)', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6 (sp)', 'R7 (ra)']
        
        for i, name in enumerate(names):
            row = tk.Frame(reg_container, bg=PinkTheme.BG_DARK)
            row.pack(fill=tk.X, pady=2)
            
            color = PinkTheme.TEXT_LIGHT if i == 0 else PinkTheme.PRIMARY
            tk.Label(row, text=name, font=('Arial', 9), width=10,
                    bg=PinkTheme.BG_DARK, fg=color, anchor='w').pack(side=tk.LEFT)
            
            lbl = tk.Label(row, text="0x0000 (0)", font=('Consolas', 10), width=14,
                          bg=PinkTheme.WHITE, fg=PinkTheme.TEXT, anchor='e',
                          padx=8, pady=3, relief=tk.SUNKEN, bd=1)
            lbl.pack(side=tk.RIGHT)
            self.reg_labels[i] = lbl
        
        # PC
        pc_frame = tk.Frame(frame, bg=PinkTheme.PRIMARY)
        pc_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        pc_inner = tk.Frame(pc_frame, bg=PinkTheme.PRIMARY)
        pc_inner.pack(fill=tk.X, padx=10, pady=8)
        
        tk.Label(pc_inner, text="📍 PC:", font=('Arial', 10, 'bold'),
                bg=PinkTheme.PRIMARY, fg='white').pack(side=tk.LEFT)
        
        self.pc_label = tk.Label(pc_inner, text="0x0000", font=('Consolas', 14, 'bold'),
                                bg=PinkTheme.PRIMARY, fg='white')
        self.pc_label.pack(side=tk.RIGHT)
        
        # Stats
        stats_frame = tk.Frame(frame, bg=PinkTheme.BG_DARK)
        stats_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Cycle
        cycle_box = tk.Frame(stats_frame, bg=PinkTheme.SECONDARY)
        cycle_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        tk.Label(cycle_box, text="🔄 Cycle:", font=('Arial', 9),
                bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT).pack(side=tk.LEFT, padx=8, pady=5)
        self.cycle_label = tk.Label(cycle_box, text="0", font=('Consolas', 11, 'bold'),
                                   bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT)
        self.cycle_label.pack(side=tk.RIGHT, padx=8, pady=5)
        
        # CPI
        cpi_box = tk.Frame(stats_frame, bg=PinkTheme.SECONDARY)
        cpi_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        tk.Label(cpi_box, text="📈 CPI:", font=('Arial', 9),
                bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT).pack(side=tk.LEFT, padx=8, pady=5)
        self.cpi_label = tk.Label(cpi_box, text="0.00", font=('Consolas', 11, 'bold'),
                                 bg=PinkTheme.SECONDARY, fg=PinkTheme.TEXT)
        self.cpi_label.pack(side=tk.RIGHT, padx=8, pady=5)
    
    def _create_machine_code_panel(self, parent):
        frame = self._create_panel(parent, "🔢 Machine Code")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.mcode_text = scrolledtext.ScrolledText(
            frame, width=32, height=10, font=('Consolas', 9),
            bg=PinkTheme.WHITE, state='disabled'
        )
        self.mcode_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _create_imem_panel(self, parent):
        frame = self._create_panel(parent, "📜 Instruction Memory")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.imem_text = scrolledtext.ScrolledText(
            frame, width=38, height=10, font=('Consolas', 9),
            bg=PinkTheme.WHITE, state='disabled'
        )
        self.imem_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _create_dmem_panel(self, parent):
        frame = self._create_panel(parent, "💾 Data Memory")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.dmem_text = scrolledtext.ScrolledText(
            frame, width=25, height=10, font=('Consolas', 9),
            bg=PinkTheme.WHITE, state='disabled'
        )
        self.dmem_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def _create_status_bar(self):
        status_frame = tk.Frame(self.root, bg=PinkTheme.PRIMARY)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_var = tk.StringVar(value="✅ Hazır - F5: Assemble | F7: Adım | F9: Çalıştır | F2: Reset")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                    bg=PinkTheme.PRIMARY, fg='white',
                                    font=('Arial', 10), anchor='w', padx=15, pady=8)
        self.status_label.pack(fill=tk.X)
    
    def _default_program(self):
        return """# 🌸 RISC-16 Assembly
# Örnek: 1'den 5'e toplam

    addi r1, r0, 5      # counter = 5
    addi r2, r0, 0      # sum = 0

loop:
    add  r2, r2, r1     # sum += counter
    addi r1, r1, -1     # counter--
    bne  r1, r0, loop   # döngü

    sw   r2, 0(r0)      # Mem[0] = toplam
    sw   r1, 2(r0)      # Mem[2] = sayac
    halt                # dur

# Sonuç: R2 = 15 (5+4+3+2+1)
"""
    
    def _update_speed(self, val):
        self.step_delay = int(val)
        hz = 1000 / self.step_delay if self.step_delay > 0 else 0
        self.speed_label.config(text=f"{self.step_delay} ms")
        self.hz_label.config(text=f"({hz:.1f} Hz)")
    
    def _update_display(self):
        # Registers
        for i in range(8):
            val = self.cpu.reg_file.read(i)
            self.reg_labels[i].config(text=f"0x{val:04X} ({val})")
            
            if val != self.prev_regs[i]:
                self.reg_labels[i].config(bg=PinkTheme.SECONDARY)
            else:
                self.reg_labels[i].config(bg=PinkTheme.WHITE)
            self.prev_regs[i] = val
        
        # PC
        self.pc_label.config(text=f"0x{self.cpu.pc:04X}")
        
        # Stats
        stats = self.cpu.get_statistics()
        self.cycle_label.config(text=str(stats['cycles']))
        self.cpi_label.config(text=f"{stats['cpi']:.2f}")
        
        # Pipeline
        info = self.cpu.get_cycle_info()
        if info:
            self.pipeline_labels['IF'].config(text=disassemble(info.if_instruction) or "---")
            self.pipeline_labels['ID'].config(text=disassemble(info.id_instruction) or "---")
            self.pipeline_labels['EX'].config(text=disassemble(info.ex_instruction) or "---")
            self.pipeline_labels['MEM'].config(text=disassemble(info.mem_instruction) or "---")
            self.pipeline_labels['WB'].config(text=disassemble(info.wb_instruction) or "---")
            
            # Hazard
            if info.stall:
                self.hazard_frame.config(bg=PinkTheme.STALL)
                self.hazard_label.config(text="🔴 STALL - Load-Use Hazard",
                                        bg=PinkTheme.STALL, fg='white')
            elif info.flush:
                self.hazard_frame.config(bg=PinkTheme.FLUSH)
                self.hazard_label.config(text="🟠 FLUSH - Branch Taken",
                                        bg=PinkTheme.FLUSH, fg='white')
            elif info.forward_a != "None" or info.forward_b != "None":
                fwd = []
                if info.forward_a != "None": fwd.append(f"A:{info.forward_a}")
                if info.forward_b != "None": fwd.append(f"B:{info.forward_b}")
                self.hazard_frame.config(bg=PinkTheme.FORWARD)
                self.hazard_label.config(text=f"🟢 FORWARD - {', '.join(fwd)}",
                                        bg=PinkTheme.FORWARD, fg='white')
            else:
                self.hazard_frame.config(bg=PinkTheme.SECONDARY)
                self.hazard_label.config(text="✅ None",
                                        bg=PinkTheme.SECONDARY, fg=PinkTheme.FORWARD)
        else:
            for stage in self.pipeline_labels:
                self.pipeline_labels[stage].config(text="---")
            self.hazard_frame.config(bg=PinkTheme.SECONDARY)
            self.hazard_label.config(text="✅ None",
                                    bg=PinkTheme.SECONDARY, fg=PinkTheme.FORWARD)
        
        # Memory
        self._update_memory()
    
    def _update_memory(self):
        # Machine Code
        self.mcode_text.config(state='normal')
        self.mcode_text.delete('1.0', tk.END)
        for addr in range(0, 64, 2):
            try:
                word = self.cpu.imem.read_word(addr)
                if word != 0:
                    marker = "▶" if addr == self.cpu.pc else " "
                    binary = format_binary(word)
                    self.mcode_text.insert(tk.END, f"{marker} {addr//2+1}| 0x{addr:04X}: 0x{word:04X}\n")
                    self.mcode_text.insert(tk.END, f"    {binary}\n")
            except:
                pass
        self.mcode_text.config(state='disabled')
        
        # Instruction Memory
        self.imem_text.config(state='normal')
        self.imem_text.delete('1.0', tk.END)
        for addr in range(0, 64, 2):
            try:
                word = self.cpu.imem.read_word(addr)
                if word != 0:
                    marker = "▶" if addr == self.cpu.pc else " "
                    asm = disassemble(word)
                    self.imem_text.insert(tk.END, f"{marker} 0x{addr:04X}: 0x{word:04X} {asm}\n")
            except:
                pass
        self.imem_text.config(state='disabled')
        
        # Data Memory
        self.dmem_text.config(state='normal')
        self.dmem_text.delete('1.0', tk.END)
        has_data = False
        for addr in range(0, 64, 2):
            try:
                word = self.cpu.dmem.read_word(addr)
                if word != 0:
                    self.dmem_text.insert(tk.END, f"0x{addr:04X}: {word} (0x{word:04X})\n")
                    has_data = True
            except:
                pass
        if not has_data:
            self.dmem_text.insert(tk.END, "(boş)")
        self.dmem_text.config(state='disabled')
    
    def _assemble(self):
        src = self.code_editor.get('1.0', tk.END)
        try:
            code = self.assembler.assemble(src)
            self.cpu.reset()
            self.cpu.load_program(code)
            self.prev_regs = [0] * 8
            self._update_display()
            self.status_var.set(f"✅ Assemble başarılı: {len(code)} instruction yüklendi")
        except Exception as e:
            messagebox.showerror("Assemble Hatası", str(e))
            self.status_var.set(f"❌ Hata: {e}")
    
    def _step(self):
        if not self.cpu.is_finished:
            self.cpu.step()
            self._update_display()
            self.status_var.set(f"👣 Cycle {self.cpu.get_statistics()['cycles']}")
        else:
            self.status_var.set("🏁 Program tamamlandı!")
    
    def _step_back(self):
        """Bir adım geri git"""
        if self.cpu.can_step_back():
            self.cpu.step_back()
            self._update_display()
            cycle = self.cpu.get_statistics()['cycles']
            self.status_var.set(f"◀ Geri: Cycle {cycle}")
        else:
            self.status_var.set("⚠️ Geri gidilecek adım yok!")
    
    def _run(self):
        self.running = True
        self.status_var.set("🚀 Çalışıyor...")
        self._run_step()
    
    def _run_step(self):
        if self.running and not self.cpu.is_finished:
            self.cpu.step()
            self._update_display()
            self.root.after(self.step_delay, self._run_step)
        else:
            self.running = False
            if self.cpu.is_finished:
                stats = self.cpu.get_statistics()
                self.status_var.set(f"🏁 Tamamlandı! Cycle: {stats['cycles']}, CPI: {stats['cpi']:.2f}")
    
    def _stop(self):
        self.running = False
        self.status_var.set("⏹ Durduruldu")
    
    def _reset(self):
        self.running = False
        self.cpu.reset()
        self.prev_regs = [0] * 8
        self._update_display()
        self.status_var.set("🔄 Reset yapıldı")
    
    def _open_file(self):
        f = filedialog.askopenfilename(filetypes=[("Assembly", "*.asm"), ("All", "*.*")])
        if f:
            with open(f, 'r') as file:
                self.code_editor.delete('1.0', tk.END)
                self.code_editor.insert('1.0', file.read())
            self.status_var.set(f"📂 Dosya açıldı: {f}")
    
    def _save_file(self):
        f = filedialog.asksaveasfilename(defaultextension=".asm",
                                        filetypes=[("Assembly", "*.asm")])
        if f:
            with open(f, 'w') as file:
                file.write(self.code_editor.get('1.0', tk.END))
            self.status_var.set(f"💾 Kaydedildi: {f}")
    
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app = MainWindow()
    app.run()
