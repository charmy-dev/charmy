import charmy as cm


window = cm.Window(size=(300, 160))
window.title = "Button test"

button = cm.TextButton(window, text="Hit me") .place((10, 10))
# window.bind("mouse_press", lambda e: print(e["mods"]))


cm.mainloop()
