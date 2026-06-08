PERFORMANCE_STATS: bool = False
MEM_STATS: bool = False


import charmy as cm
if PERFORMANCE_STATS:
    import cProfile
if MEM_STATS:
    import tracemalloc
    tracemalloc.start()


window = cm.Window(size=(300, 160))
window.title = "Button test"

button = cm.Button(window, text="Hit me", on_click=lambda: print("Button clicked!"))
button.place((10, 10))


if MEM_STATS:
    @button.on(cm.event_types.MouseClick)
    def print_mem(event: cm.event_types.MouseClick):
        snapshot = tracemalloc.take_snapshot()

        for stat in snapshot.statistics("lineno")[:20]:
            print(stat)
        
        print("\n=========================\n")


if PERFORMANCE_STATS:
    cProfile.run("cm.mainloop()", sort="cumtime")
else:
    cm.mainloop()

sizes = []