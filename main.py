from charmy import Button, Window, mainloop

window1 = Window(size=(300, 400))

with window1:
    Button().place(0, 0, 100, 100)
    Button().place(100, 100, 100, 100)

mainloop()
