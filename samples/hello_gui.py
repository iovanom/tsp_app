import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Hello World")
    label = tk.Label(root, text="Hello World", font=("Arial", 24))
    label.pack(pady=20)
    button = tk.Button(root, text="Close", command=root.quit)
    button.pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()