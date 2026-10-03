PERFORMANCE_STATS: bool = False
MEM_STATS: bool = False
TEST_WIDGET_MOVE: bool = True


import charmy as cm


if PERFORMANCE_STATS:
    import cProfile
if MEM_STATS:
    import tracemalloc
    tracemalloc.start()


window = cm.Window(size=(300, 160))
window.title = "Button test"

text = cm.Text(window, text="Hi, I`m just a text label!")
text.place((10, 10))

if PERFORMANCE_STATS:
    cProfile.run("cm.mainloop()", sort="cumtime")
else:
    cm.mainloop()

sizes = []