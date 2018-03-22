


def convert_to_jcode(hpgl_text:str, steps_per_mm=1):
    result = ""
    hpgl_lines = hpgl_text.replace("\n", "").split(";")
    for line in hpgl_lines:
        if line.startswith("IN"):
            result += "ZE\n"
        elif line.startswith(("PU", "PD")):
            if line.startswith("PU"):
                move = True
                result += "PU\n"
            else:
                move = False
                result += "PD\n"
            coords = line[2:].split(",")
            if len(coords) % 2:
                raise Exception("Coordinates must be provided in pairs")
            else:
                coords = [coords[i:i+2] for i  in range(0, len(coords), 2)]
                for coord in coords:
                    if move:
                        result += "GT "
                    else:
                        result += "LN "
                    for i in range(len(coord)):
                        coord[i] = int(coord[i]) / steps_per_mm
                        print(len(coord))
                    result += "{0} {1}\n".format(*coord)
        else:
            print("Skipping unknown command {}".format(line))

    return result
                

