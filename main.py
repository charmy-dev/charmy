from charmy import mainloop, Window, Button

window1 = Window(size=(300, 400))

window1.config(title = "Button test")

button = Button()

window2 = Window(size=(500, 600))

window2.config(title="muti-window test")
import threading
print(threading._count())

mainloop()