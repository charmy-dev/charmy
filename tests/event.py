import charmy as cm

win = cm.Window()
win.title = "Event Test"

print_event_type = lambda event: print(event.type)

win.bind(cm.event_types.MousePress, print_event_type)
win.bind(cm.event_types.MouseRelease, print_event_type)
# win.bind(cm.event_types.MouseMove, print_event_type)
win.bind(cm.event_types.MoveEvent, print_event_type)
win.bind(cm.event_types.ResizeEvent, print_event_type)
win.bind(cm.event_types.FocusGain, print_event_type)
win.bind(cm.event_types.FocusLoss, print_event_type)

cm.mainloop()