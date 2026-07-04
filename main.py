from charmy import Button, Window, mainloop

window1 = Window(size=(300, 200))
window1.title = "Charmy GUI"

with window1:
    Button().place((0, 0), (100, 100))
    Button().place((100, 100), (100, 100))

mainloop()
