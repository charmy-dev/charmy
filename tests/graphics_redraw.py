import charmy as cm
import time

window = cm.Window(size=(540, 480))
window.title = "Graphics Redraw"
window.background = (200, 200, 200)


# region Shapes

test_rounded_rect = cm.graphics.DrawnShape(window, cm.styles.shape.RoundRect(
    (0, 0), (150, 100), 25), (150, 150, 255), offset=(150, 100)) .draw()

test_rounded_rect_2 = cm.graphics.DrawnShape(window, cm.styles.shape.RoundRect(
    (230, 150), (150, 100), 25), (255, 255, 0, 0.2)) .draw()

# region Texts
test_text = cm.graphics.DrawnText(
    window, 
    "In this test, prop of round rect 1 keeps changing", 
    cm.styles.text_style.TextStyle(
        font="Consolas", 
        size=18, 
        underlined=True, 
        # strikethrough=True, 
        ), 
    (0, 0, 0), 
    (30, 350), 
    ) .draw()

# endregion

manager = window.parent

colors = [(255, 0, 0), (0, 0, 255), (0, 255, 0)]
frames = 0
color_pointer = 0

while window._alive:
    manager.update()
    time.sleep(0.01)
    frames += 1
    if frames % 100 == 0:
        print("Texture of round rect 1 updated.")
        test_rounded_rect.texture = colors[color_pointer % 3]
        color_pointer += 1
        test_rounded_rect.draw() # This was designed like this!!!
        # How I forgot this??