import charmy as cm


window = cm.Window(size=(300, 160))
window.title = "Button test"

button = cm.Button(window, text="Hit me")
button.place((10, 10))

cm.mainloop()
