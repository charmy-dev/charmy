import charmy as cm

window = cm.Window()
window.title = "Validation for Shape Hit Test Function"

cm.graphics.DEBUG_FLAGS.DRAW_OBJECTS_BOUNDARY = True

test_shape = cm.graphics.DrawnShape(
    cm.styles.shape.AnyShape(
        [
            cm.styles.shape.PolyLine(
                [(50, 50), (70, 200), (420, 270), (170, 330), (350, 120), (200, 80)]
            ),
            cm.styles.shape.CubicBezier(
                [
                    (200, 80),
                    (150, 150),
                    (120, 150),
                    (50, 50),
                ]
            ),
        ]
    ),
    None,
    5,
    (255, 0, 0),
).draw(window)

shape_boundary = test_shape.boundary


def draw_within():
    for y in range(shape_boundary[0][1], shape_boundary[0][1] + shape_boundary[1][1] + 1, 5):
        for x in range(shape_boundary[0][0], shape_boundary[0][0] + shape_boundary[1][0] + 1, 5):
            if (x, y) in test_shape.shape:
                cm.graphics.DrawnShape(
                    cm.styles.shape.Rect((0, 0), (3, 3)), (0, 0, 200), offset=(x, y)
                ).draw(window)


draw_within()

cm.mainloop()
