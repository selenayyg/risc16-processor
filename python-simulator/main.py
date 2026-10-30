#!/usr/bin/env python3
"""RISC-16 Simulator - Ana giriş noktası"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.core.cpu import CPU
from src.assembler.encoder import Assembler
from src.utils.helpers import disassemble, format_hex

def run_cli(args):
    cpu = CPU()
    assembler = Assembler()
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                source = f.read()
            machine_code = assembler.assemble(source)
            cpu.load_program(machine_code)
            print(f"Program yüklendi: {args.file}")
            print(f"Instruction sayısı: {len(machine_code)}\n")
            
            if args.listing:
                print(assembler.get_listing())
                print()
        except FileNotFoundError:
            print(f"Hata: Dosya bulunamadı: {args.file}")
            return
        except Exception as e:
            print(f"Hata: {e}")
            return
    
    if args.run:
        print("=" * 50)
        print("Simülasyon başlatılıyor...")
        print("=" * 50)
        
        cpu.run(max_cycles=args.max_cycles)
        
        stats = cpu.get_statistics()
        print(f"\nSimülasyon tamamlandı!")
        print(f"Toplam cycle: {stats['cycles']}")
        print(f"Çalıştırılan instruction: {stats['instructions']}")
        print(f"CPI: {stats['cpi']:.2f}")
        print(f"Stall sayısı: {stats['stalls']}")
        print(f"Flush sayısı: {stats['flushes']}")
        print(f"\nRegister durumu:")
        print(cpu.reg_file)
        
        if args.verbose:
            print(f"\nData Memory (non-zero):")
            print(cpu.dmem)
    
    elif args.step:
        print("Adım adım mod (q: çık, Enter: devam)")
        print("=" * 50)
        
        while not cpu.is_finished:
            cycle_info = cpu.step()
            
            print(f"\nCycle {cycle_info.cycle}:")
            print(f"  PC: {format_hex(cycle_info.pc)}")
            print(f"  IF:  {disassemble(cycle_info.if_instruction)}")
            print(f"  ID:  {disassemble(cycle_info.id_instruction)}")
            print(f"  EX:  {disassemble(cycle_info.ex_instruction)}")
            print(f"  MEM: {disassemble(cycle_info.mem_instruction)}")
            print(f"  WB:  {disassemble(cycle_info.wb_instruction)}")
            
            if cycle_info.stall: print(f"  ** STALL **")
            if cycle_info.flush: print(f"  ** FLUSH **")
            
            cmd = input("\n[Enter/q]: ").strip().lower()
            if cmd == 'q': break
        
        print(f"\nFinal Register durumu:")
        print(cpu.reg_file)

def run_gui():
    try:
        from gui.main_window import MainWindow
        app = MainWindow()
        app.run()
    except ImportError as e:
        print(f"GUI modülü yüklenemedi: {e}")
        print("CLI modunu kullanın: python main.py --help")

def main():
    parser = argparse.ArgumentParser(description='RISC-16 İşlemci Simülatörü')
    parser.add_argument('-f', '--file', help='Assembly dosyası')
    parser.add_argument('-r', '--run', action='store_true', help='Programı çalıştır')
    parser.add_argument('-s', '--step', action='store_true', help='Adım adım çalıştır')
    parser.add_argument('-l', '--listing', action='store_true', help='Assembly listing göster')
    parser.add_argument('-v', '--verbose', action='store_true', help='Detaylı çıktı')
    parser.add_argument('-m', '--max-cycles', type=int, default=1000, help='Maksimum cycle')
    parser.add_argument('--gui', action='store_true', help='GUI başlat')
    
    args = parser.parse_args()
    
    if args.gui:
        run_gui()
    elif args.file:
        run_cli(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
