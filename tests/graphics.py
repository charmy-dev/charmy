import cProfile

import charmy as cm

window = cm.Window(size=(540, 480))
window.title = "Graphics"
window.background = (200, 200, 200)


# region Lines
test_polyline = cm.graphics.DrawnLine(
    cm.styles.shape.PolyLine([(500, 10), (50, 150), (200, 300), (70, 30)]), (255, 100, 100)
).draw(window)
test_arc = cm.graphics.DrawnLine(
    cm.styles.shape.CircleArc((100, 100), 50, 0, 290), (100, 100, 255)
).draw(window)
test_arc_2 = cm.graphics.DrawnLine(
    cm.styles.shape.CircleArc((200, 100), 50, 320, 50), (100, 100, 255)
).draw(window)
test_quadratic_bezier = cm.graphics.DrawnLine(
    cm.styles.shape.QuadraticBezier([(100, 150), (250, 250), (-40, 350)]),
    (100, 255, 100, 100),
    width=8,
).draw(window)


# region Shapes
test_rect = cm.graphics.DrawnShape(
    cm.styles.shape.Rect((300, 300), (100, 80)), (0, 255, 255), 3, (255, 0, 0)
).draw(window)

test_polygon = cm.graphics.DrawnShape(
    cm.styles.shape.AnyShape(
        [
            cm.styles.shape.PolyLine(
                [(400, 400), (450, 400), (470, 430), (420, 450), (350, 420), (400, 400)]
            )
        ]
    ),
    (150, 150, 150),
    5,
    (255, 0, 0),
).draw(window)

test_rounded_rect = cm.graphics.DrawnShape(
    cm.styles.shape.RoundRect((0, 0), (150, 100), 25), (150, 150, 255), offset=(300, 100)
).draw(window)

test_rounded_rect_2 = cm.graphics.DrawnShape(
    cm.styles.shape.RoundRect((350, 150), (150, 100), 25), (255, 255, 0, 50)
).draw(window)

# region Texts
test_text = cm.graphics.DrawnText(
    "Hello, this CHARMY world!",
    cm.styles.text_style.TextStyle(
        font="Consolas",
        size=24,
        weight=cm.styles.text_style.WEIGHT.EXTRALIGHT,
        underlined=True,
        # strikethrough=True,
    ),
    (0, 0, 0),
    (200, 250),
).draw(window)

# endregion


cProfile.run("cm.mainloop()", sort="cumtime")
