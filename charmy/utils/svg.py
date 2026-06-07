from __future__ import annotations as _

import re as _re

from ..styles import shape as _shape

__all__ = ["shapes_from_svg_path"]


class CharmySVGIntepreterError(Exception): ...


@staticmethod
def shapes_from_svg_path(svg_path: str, scale: float = 1) -> _shape.AnyShape | _shape.ShapeGroup:
    """This converts SVG path into sequence of Charmy lines.

    I made a fucking complete SVG path intepreter man!!!   —— rgzz666 @ 26/05/16

    We assume that the SVG path that you give is valid, otherwise we will throw an error.

    :param svg_path: The SVG path in string
    """

    def tokenize_svg_path(path_string):
        # This regex matches:
        # 1. Any SVG command letter: [a-zA-Z]
        # 2. Any integer/floating point number (including negatives): -?\d*\.?\d+
        token_pattern = _re.compile(r"([a-zA-Z]|-?\d*\.?\d+)")
        # Find all matching tokens in the string
        tokens = token_pattern.findall(path_string)
        return tokens

    def calc_point(sections: list[str], curr: int, offset: int, relative: bool):
        point_x = float(sections[curr + offset])
        point_y = float(sections[curr + offset + 1])
        if relative:
            return pen_pos[0] + point_x, pen_pos[1] + point_y
        else:
            return point_x, point_y

    def scale_point(point: tuple[int | float, int | float], scale: float = scale) -> _shape.Point:
        return (int(round(point[0] * scale, 0)), int(round(point[1] * scale, 0)))

    def calc_s_curve(
        prev_curve: _shape.CubicBezier,
        s_data: list[tuple[int, int]],
    ) -> _shape.CubicBezier:
        """
        Calculates and returns a new _shape.CubicBezier object for an S/s command.

        :param prev_curve: The preceding _shape.CubicBezier object (in absolute coordinates).
        :param s_data: A list of 2 tuples representing the points provided to the S/s command:
                    [(cp2_x, cp2_y), (end_x, end_y)]
                    These can be absolute or relative depending on the `relative` flag.
        :param relative: True if the current command is lowercase 's', False if uppercase 'S'.
        """
        # 1. Extract the crucial points from the previous absolute curve
        # The end of the previous curve is the start (junction) of the new curve
        junc_x, junc_y = prev_curve.points[3]
        old_cp2_x, old_cp2_y = prev_curve.points[2]
        # 2. Calculate the mirrored first control point (always absolute)
        # Formula: 2 * Junction - Old_Control__shape.Point
        new_cp1_x = 2 * junc_x - old_cp2_x
        new_cp1_y = 2 * junc_y - old_cp2_y
        new_cp1 = (new_cp1_x, new_cp1_y)
        # 3. Unpack the incoming S/s command data
        s_cp2, s_end = s_data
        # 4. Resolve the S/s points to absolute coordinates if they are relative
        # if relative:
        #     abs_cp2 = (junc_x + s_cp2[0], junc_y + s_cp2[1])
        #     abs_end = (junc_x + s_end[0], junc_y + s_end[1])
        # else:
        abs_cp2 = s_cp2
        abs_end = s_end
        # 5. Construct and return the new absolute _shape.CubicBezier object
        # Order: [start, control_1, control_2, end]
        return _shape.CubicBezier([(junc_x, junc_y), new_cp1, abs_cp2, abs_end])

    sections: list[str] = tokenize_svg_path(svg_path)
    command_index: int = 0
    pen_pos: _shape.Point = (0, 0)
    lines: list[_shape.LinePath] = []
    shapes: list[_shape.AnyShape] = []
    while command_index < len(sections):
        command = sections[command_index]
        match command.upper():
            case "M":  # MoveTo
                # End current shape
                if len(lines) > 0:
                    shapes.append(_shape.AnyShape(lines))
                    lines = []
                # Then set pos
                pen_pos = scale_point(calc_point(sections, command_index, 1, command.islower()))
                command_index += 3
            case "L" | "V" | "H":  # LineTo
                dest: _shape.Point
                match command.upper():
                    case "L":  # Any line
                        dest = scale_point(
                            calc_point(sections, command_index, 1, command.islower())
                        )
                    case "V":  # Vertical
                        dest = scale_point(
                            (
                                pen_pos[0],
                                float(sections[command_index + 1])
                                + (pen_pos[1] if command.isupper() else 0),
                            )
                        )
                    case "H":  # Horizontal
                        dest = scale_point(
                            (
                                float(sections[command_index + 1])
                                + (pen_pos[0] if command.isupper() else 0),
                                pen_pos[1],
                            )
                        )
                lines.append(_shape.Line([pen_pos, dest]))
                pen_pos = dest
                command_index += 3
            case "C" | "S":  # Cubic Bezier
                if command.upper() == "S":
                    # Chained cubic Beziers (chained smooth curves)
                    if not isinstance(lines[-1], _shape.CubicBezier):
                        raise CharmySVGIntepreterError(
                            "An S command must follow a C command in SVG path."
                        )
                    lines.append(
                        calc_s_curve(
                            lines[-1],
                            [
                                scale_point(
                                    calc_point(sections, command_index, 1, command.islower())
                                ),
                                scale_point(
                                    calc_point(sections, command_index, 3, command.islower())
                                ),
                            ],
                        )
                    )
                    command_index += 5
                else:
                    # Normal cubic Beziers
                    lines.append(
                        _shape.CubicBezier(
                            [
                                pen_pos,
                                scale_point(
                                    calc_point(sections, command_index, 1, command.islower())
                                ),
                                scale_point(
                                    calc_point(sections, command_index, 3, command.islower())
                                ),
                                scale_point(
                                    calc_point(sections, command_index, 5, command.islower())
                                ),
                            ]
                        )
                    )
                    command_index += 7
                pen_pos = lines[-1].end_point
            case "Z":  # Close path
                # Close path
                lines.append(_shape.Line([pen_pos, lines[0].start_point]))
                # End current shape
                if len(lines) > 0:
                    shapes.append(_shape.AnyShape(lines))
                    lines = []
                # Then to next command
                command_index += 1
            case _:
                # TODO: Support quadratic Beziers and oval arcs
                raise CharmySVGIntepreterError(f"Invalid or unsupported command: {command}.")
    if len(shapes) == 1:
        return shapes[0]
    else:
        return _shape.ShapeGroup(shapes)
