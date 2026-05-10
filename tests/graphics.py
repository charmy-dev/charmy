import charmy as cm


window = cm.Window(size=(540, 480))
window.title = "Graphics"

test_polyline = cm.shape.PolyLine([
    (500, 10), (50, 150), (200, 300), (70, 30)
    ]) .draw(window, (255, 100, 100))
test_arc = cm.shape.CircleArc((100, 100), 50, 0, 290) .draw(window, (100, 100, 255))
test_quadratic_bezier = cm.shape.QuadraticBezier([
    (150, 200), (300, 300), (10, 400)
    ]) .draw(window, (100, 255, 100, 100), width=2)


test_rect = cm.shape.Rect((300, 300), (100, 80)) .draw(window, (0, 255, 255), 3, (255, 0, 0))

test_polygon = cm.shape.AnyShape([cm.shape.PolyLine([
    (400, 400), (450, 400), (470, 430), (420, 450), (350, 420), (400, 400)
    ])]) .draw(window, (150, 150, 150), 5, (255, 0, 0))

test_rounded_rect = cm.shape.RoundRect(
    (300, 100), (150, 100), 25) .draw(window, (150, 150, 255))


test_text = cm.draw.DrawnText(
    "Hello, this CHARMY world!", 
    cm.styles.text_style.TextStyle(font="Consolas", size=24), 
    (200, 250), 
    (255, 255, 255), 
    ) .draw(window)


cm.mainloop()