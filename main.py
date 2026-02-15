from charmy import *

app = App()
window = Window(size=(300, 160))

window.bind("resize", lambda event: print(f"<{event.event_type}>"))
window.bind("move", lambda event: print(f"<{event.event_type}>"))

print(window)

app.run()
