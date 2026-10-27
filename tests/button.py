PERFORMANCE_STATS: bool = False
MEM_STATS: bool = False
TEST_WIDGET_MOVE: bool = False
CREATE_BTN_ON_CLICK: bool = False


import charmy as cm

cm.DEBUG_FLAGS.PRINT_REDRAWN_OBJ_IDS = True


if PERFORMANCE_STATS:
    import cProfile
if MEM_STATS:
    import tracemalloc
    tracemalloc.start()


window = cm.Window(size=(300, 160))
window.title = "Button test"

button = cm.Button(window, text="Hit me!", on_click=lambda: print("Button clicked!"))
button.place((10, 10))

styled_button = cm.Button(
    window, 
    text="Fancy dumb", 
    profiles={
        "default": cm.button.ButtonProfile(
            size=(100, 30), 
            shape=cm.styles.shape.RoundRect(
                (0, 0), cm.profile_ref("widget.size"), 5
                ), 
            background=cm.styles.texture.LinearGradient(
                (0, 0), (0, cm.profile_ref("widget.height")), {
                    0: (180, 180, 180), 
                    .05: (230, 230, 230), 
                    .3: (240, 240, 240), 
                    .5: (230, 230, 230), 
                    1: (180, 180, 180), 
                    }
                ), 
            border_width = 1, 
            border_texture = (200, 200, 200), 
            ), 
        "hover": cm.button.ButtonProfile(
            background=cm.styles.texture.LinearGradient(
                (0, cm.profile_ref("widget.height")), (0, 0), {
                    0: (40, 40, 40), 
                    .05: (130, 130, 130), 
                    .3: (140, 140, 140), 
                    .5: (130, 130, 130), 
                    1: (60, 60, 60), 
                    }
                )
            ), 
        }, 
    )
styled_button.place((150, 10))


if MEM_STATS:
    @button.on(cm.event_types.MouseClick)
    def print_mem(_: cm.event_types.MouseClick):
        snapshot = tracemalloc.take_snapshot()

        for stat in snapshot.statistics("lineno")[:20]:
            print(stat)
        
        print("\n=========================\n")

if TEST_WIDGET_MOVE:
    @button.on(cm.event_types.MouseClick)
    def move_button(_: cm.event_types.MouseClick):
        old = button.layout_profile.pos
        button.layout_profile.pos = old[0] + 10, old[1] + 10

if CREATE_BTN_ON_CLICK:
    dummy_button_count = 0
    @button.on(cm.event_types.MouseClick)
    def create_button(_: cm.event_types.MouseClick):
        global window, dummy_button_count
        cm.Button(window, "Dumb button").place((
            dummy_button_count // 5 * 10 + dummy_button_count % 5 * 10 + 30, 
            dummy_button_count % 5 * 10 + 50
            ))
        dummy_button_count += 1


if PERFORMANCE_STATS:
    cProfile.run("cm.mainloop()", sort="cumtime")
else:
    cm.mainloop()

sizes = []