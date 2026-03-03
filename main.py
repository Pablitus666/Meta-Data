from tkinterdnd2 import TkinterDnD
from ui.app import MetadataApp

def main():
    # Usamos TkinterDnD.Tk en lugar de tk.Tk para habilitar Drag & Drop
    root = TkinterDnD.Tk()
    app = MetadataApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
