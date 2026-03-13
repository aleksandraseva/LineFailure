from Lines.models.Line import Line

line_list = ["LL10", "LL2"]


def add_line():
    global line_list
    for line_name in line_list:
        line = Line(name=line_name)
        line.save()
