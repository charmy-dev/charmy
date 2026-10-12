import charmy as cm

win = cm.Window()

test_gradient = cm.styles.texture.LinearGradient(
    (0, 0), (50, 100), 
    {
        0: (100, 0, 0), 
        1: (0, 0, 100)
    }
    )

test_rect = cm.graphics.DrawnShape(
    win, 
    cm.styles.shape.Rect((20, 20), (100, 100)), 
    test_gradient, 
    ) .draw()

cm.mainloop()