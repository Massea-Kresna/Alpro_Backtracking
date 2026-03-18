import tkinter as tk
import sys
import os

def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, base_dir)

    from visualization import MazeVisualizer

    root = tk.Tk()

    #default maze: 15 baris × 21 kolom
    app = MazeVisualizer(root, rows=15, cols=21)

    #center window di layar
    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    root.geometry(f"+{x}+{y}")
    root.mainloop()

if __name__ == "__main__":
    main()