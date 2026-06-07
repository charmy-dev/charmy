import charmy as cm


window = cm.Window(size=(300, 160))
window.title = "Button test"

button = cm.Button(window, text="Hit me", on_click=lambda: print("Button clicked!"))
button.place((10, 10))


@button.on(cm.event_types.MouseEnter)
def print_press(event: cm.event_types.MouseEnter):
    print(f"Mouse entered")


cm.mainloop()
