import charmy as cm

window = cm.Window(size=(300, 160))
window.config(title="Button test")

button = cm.Button()
window.bind("mouse_press", lambda e: print(e["mods"]))

cm.mainloop()
