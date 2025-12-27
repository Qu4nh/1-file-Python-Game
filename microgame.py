import tkinter as tk
import random

def on_closing():
    pass

def change_color():
    color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
    label.config(fg=color)
    root.after(1000, change_color)

def spawn_enemy():
    x = random.randint(0, root.winfo_screenwidth())
    y = random.randint(0, root.winfo_screenheight())
    enemy = canvas.create_rectangle(x, y, x+30, y+30, fill="red")
    enemies.append(enemy)
    root.after(2000, spawn_enemy)

def destroy_enemy(event):
    for enemy in enemies:
        if canvas.coords(enemy)[0] < event.x < canvas.coords(enemy)[2] and \
           canvas.coords(enemy)[1] < event.y < canvas.coords(enemy)[3]:
            canvas.delete(enemy)
            enemies.remove(enemy)
            spawn_enemy()
            increase_text()

def increase_text():
    current_text = label.cget("text")
    new_text = current_text + random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdeghijklmnopqrstuvwxyz1234567890")
    label.config(text=new_text)

root = tk.Tk()
root.title("Minigame: Click để tiêu diệt kẻ địch")

root.attributes('-fullscreen', True)
root.attributes('-topmost', True)

canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
canvas.pack()

label = tk.Label(root, text="Qu4nh", font=("Helvetica", 48), padx=20, pady=10)
label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

root.protocol("WM_DELETE_WINDOW", on_closing)

change_color()

enemies = []

spawn_enemy()

canvas.bind("<Button-1>", destroy_enemy)

root.mainloop()
