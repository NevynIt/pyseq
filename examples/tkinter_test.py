import tkinter as tk
import imps.pson
import platform

tx = []
# keyb = []
# keyrow= []

def lbladd(txt):
    tx.append(txt)
    while len(tx)>15:
        del(tx[0])
    label.config(text='\n'.join(tx))

def on_key_press(event):
    # global keyb, keyrow
    # c = (event.keycode, event.keysym)
    # if len(keyrow)>0:
    #     if c == keyrow[-1]:
    #         keyb.append(keyrow)
    #         keyrow = []
    #         c = None
    # if c:
    #     keyrow.append(c)
    lbladd(f"Pre: {event}")

def on_key_release(event):
    lbladd(f"Rel: {event}")

def on_button_press(event):
    lbladd(f"Btn: {event}")

def on_button_release(event):
    lbladd(f"___: {event}")

def on_mouse_move(event):
    lbladd(f"mov: {event}")

def on_mouse_wheel(event):
    # On Windows, use event.delta
    if platform.system() == "Windows":
        delta = event.delta
    # On Unix/Linux, use event.num
    else:
        delta = -120 if event.num == 4 else 120
    lbladd(f"whl: {event}")


# Set up the main window
root = tk.Tk()
root.title("Key Press Tracker")

# Create a label to display the key press/release information
label = tk.Label(root, text="Press or release a mouse button", font=("Helvetica", 14), anchor='w', justify=tk.LEFT)
label.pack(expand=True, fill=tk.BOTH)

# Bind key press and release events to the root window
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)

root.bind("<ButtonPress-1>", on_button_press)
root.bind("<ButtonRelease-1>", on_button_release)

root.bind("<ButtonPress-2>", on_button_press)
root.bind("<ButtonRelease-2>", on_button_release)

root.bind("<ButtonPress-3>", on_button_press)
root.bind("<ButtonRelease-3>", on_button_release)

root.bind("<Motion>", on_mouse_move)

# Bind mouse wheel event
if platform.system() == "Windows":
    root.bind("<MouseWheel>", on_mouse_wheel)
else:
    root.bind("<Button-4>", on_mouse_wheel)
    root.bind("<Button-5>", on_mouse_wheel)

# Start the GUI event loop
root.mainloop()
# keyb.append(keyrow)
# imps.pson.dump(keyb, "examples\\keyb.pson")