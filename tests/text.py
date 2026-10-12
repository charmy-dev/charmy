PERFORMANCE_STATS: bool = False


import charmy as cm


if PERFORMANCE_STATS:
    import cProfile


window = cm.Window(size=(300, 160))
window.title = "Text test"

text = cm.Text(window, text="Hi, I`m just a text label!")
text.place((10, 10))

if PERFORMANCE_STATS:
    cProfile.run("cm.mainloop()", sort="cumtime")
else:
    cm.mainloop()

sizes = []