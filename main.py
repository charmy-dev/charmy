from charmy import *

app = CApp()
window = CWindow(size=(300, 160))

window.bind("on_resize", lambda event: print(f"<{event['event_type']}>"))
window.bind("on_move", lambda event: print(f"<{event['event_type']}>"))

print(window)

app.run()
