import charmy as cm

window = cm.Window(size=(300, 160))

"""window.bind(
    "resize",
    lambda event: print(f"<{event.event_type}>: {event["width"]}x{event['height']}"),
)
window.bind(
    "move",
    lambda event: print(f"<{event.event_type}>: {event["x_root"]}+{event['y_root']}"),
)
# window.bind("mouse_move", lambda event: print(f"<{event.event_type}>: {event["x"]}+{event['y']}"))
window.bind(
    "mouse_enter",
    lambda event: print(f"<{event.event_type}>"),
)
window.bind(
    "mouse_leave",
    lambda event: print(f"<{event.event_type}>"),
)
window.bind(
    "mouse_press",
    lambda event: print(f"<{event.event_type}>: {event["button"]} {event["mods"]}"),
)
window.bind(
    "mouse_release",
    lambda event: print(f"<{event.event_type}>：{event["button"]} {event["mods"]}"),
)"""
print(window.id)

widget = cm.Widget(window)
color = cm.Color()
color.set_color_rgba(0, 0, 0)
widget.add_element("rect", rect=cm.Rect(x=0, y=0, width=100, height=100), bg=color)

cm.mainloop()
