import charmy as cm

win = cm.Window()
win.title = "Charmy Linear Gradient Test"

test_gradient_1 = cm.styles.texture.LinearGradient(
    (0, 0), (50, 100), 
    {
        0: (100, 0, 0), 
        1: (0, 0, 100)
    }
    )

test_gradient_2 = cm.styles.texture.LinearGradient(
    (0, 0), (100, 100), 
    {
        0.2: (100, 0, 0, 1), 
        1: (0, 0, 100, 0.3)
    }
    )

test_gradient_3 = cm.styles.texture.LinearGradient(
    (0, 0), (100, 100), 
    {
        0: (100, 0, 0, 1), 
        0.7: (0, 0, 100, 0)
    }
    )

cm.graphics.DrawnShape(
    win, 
    cm.styles.shape.Rect((20, 20), (100, 100)), 
    test_gradient_1, 
    ) .draw()

cm.graphics.DrawnText(
    win, "TEXT BEHIND", 
    cm.styles.text_style.TextStyle(), (0, 0, 0), 
    offset=(150, 70)
    ) .draw()

cm.graphics.DrawnShape(
    win, 
    cm.styles.shape.Rect((140, 20), (100, 100)), 
    test_gradient_2, 
    ) .draw()

cm.graphics.DrawnShape(
    win, 
    cm.styles.shape.Rect((20, 140), (100, 100)), 
    test_gradient_3, 
    ) .draw()

cm.mainloop()