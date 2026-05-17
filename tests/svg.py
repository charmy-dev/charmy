import charmy as cm

window = cm.window.Window()
window.title = "Charmy SVG Path Intepreter Test"
window.background = (200, 200, 200)

APPLE_SVG = \
    "M18.71 19.5C17.88 20.74 17 21.95 15.66 21.97C14.32 22 13.89 21.18 12.37 21.18C10.84 21.18 10."\
    "37 21.95 9.09997 22C7.78997 22.05 6.79997 20.68 5.95997 19.47C4.24997 17 2.93997 12.45 4.6999"\
    "7 9.39C5.56997 7.87 7.12997 6.91 8.81997 6.88C10.1 6.86 11.32 7.75 12.11 7.75C12.89 7.75 14.3"\
    "7 6.68 15.92 6.84C16.57 6.87 18.39 7.1 19.56 8.82C19.47 8.88 17.39 10.1 17.41 12.63C17.44 15."\
    "65 20.06 16.66 20.09 16.67C20.06 16.74 19.67 18.11 18.71 19.5ZM13 3.5C13.73 2.67 14.94 2.04 1"\
    "5.94 2C16.07 3.17 15.6 4.35 14.9 5.19C14.21 6.04 13.07 6.7 11.95 6.61C11.8 5.46 12.36 4.26 13"\
    " 3.5Z"

shape = cm.styles.shape.shapes_from_svg_path(APPLE_SVG, scale=10)

apple_logo = cm.graphics.DrawnShape(
    shape, 
    (0, 0, 0)
    ) .draw(window)

# Disclaimer
cm.graphics.DrawnText(
    "DISCLAIMER", 
    cm.styles.text_style.TextStyle(
        font="Consolas", 
        size=24, 
        weight=cm.styles.text_style.WEIGHT.BOLD, 
        underlined=True, 
        ), 
    (0, 0, 0), 
    (50, 250), 
    ) .draw(window)
cm.graphics.DrawnText(
    "The Apple logo is is an Apple Inc. property.", 
    cm.styles.text_style.TextStyle(
        font="Consolas", 
        size=16, 
        ), 
    (0, 0, 0), 
    (50, 280), 
    ) .draw(window)

cm.mainloop(interval=0.011111)