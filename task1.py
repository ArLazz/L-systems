import turtle
import re
import random


# список функций для управления параметаризированными командами
# у всех функций будет префикс cmd_ и первый параметр t - черепашка
def cmd_turtle_fd(t, length, *args):
    t.pencolor('#30221A')
    t.pensize(args[1])
    t.fd(length * args[0])


def cmd_turtle_left(t, *args):
    t.left(args[0])


def cmd_turtle_right(t, *args):
    t.right(args[0])


def cmd_turtle_leaf(t, length, *args):
    if random.random() > 0.5:  # вероятность рисования листа
        return

    p = t.pensize()
    t.pensize(5)
    p = random.randint(0, 2)
    if p == 0:
        t.pencolor('#009900')
    elif p == 1:
        t.pencolor('#667900')
    else:
        t.pencolor('#20BB00')

    t.fd(length // 2)
    t.pencolor('#000000')
    t.pensize(p)


class LSystem2D:
    def __init__(self, t, axiom, width, length, angle):
        self.axiom = axiom  # инициатор
        self.state = axiom  # начальная строка
        self.width = width  # толщина
        self.length = length  # длина
        self.angle = angle  # угол
        self.t = t  # черепашка
        self.rules = {}  # правила
        self.t.pensize(self.width)
        self.key_re_list = []
        self.rules_key = None
        self.cmd_functions = {}

    def add_rules(self, *rules):
        for r in rules:
            p = 1
            if len(r) == 3:
                key, value, p = r
            else:
                key, value = r
            key_re = key.replace("(", r"\(")
            key_re = key_re.replace(")", r"\)")
            key_re = key_re.replace("+", r"\+")
            key_re = key_re.replace("-", r"\-")
            if not isinstance(value, str):
                key_re = re.sub(r"([a-z]+)([, ]*)", lambda m: r"([-+]?\b\d+(?:\.\d+)?\b)" + m.group(2), key_re)
                self.key_re_list.append(key_re)

            if not self.rules.get(key):
                self.rules[key] = [(value, key_re, p)]
            else:
                self.rules[key].append((value, key_re, p))

    def get_random_rule(self, rules):
        p = random.random()  # случайное вещественное число в интервале [0; 1]
        off = 0
        for v in rules:
            if p < (v[2] + off):
                return v
            off += v[2]
        return rules[0]

    def add_rules_move(self, *moves):
        for key, func in moves:
            self.cmd_functions[key] = func

    def update_param_cmd(self, m):
        if not self.rules_key:
            return ""
        rule = self.rules_key[0] if len(self.rules_key) == 1 else self.get_random_rule(self.rules_key)

        if isinstance(rule[0], str):
            return rule[0].lower()
        else:
            args = list(map(float, m.groups()))
            return rule[0](*args).lower()

    def generate_path(self, n_iter):
        for n in range(n_iter):
            for key, rules in self.rules.items():
                self.rules_key = rules
                self.state = re.sub(rules[0][1], self.update_param_cmd, self.state)
                self.rules_key = None
            self.state = self.state.upper()

    def set_turtle(self, my_tuple):
        self.t.up()
        self.t.goto(my_tuple[0], my_tuple[1])
        self.t.seth(my_tuple[2])
        self.t.down()

    def draw_turtle(self, start_pos, start_angle):
        turtle.tracer(1, 0)  # форсажный режим для черепашки
        self.t.up()
        self.t.setpos(start_pos)  # стартовая позиция
        self.t.seth(start_angle)  # начальный угол
        self.t.down()  # черепашка опускается на "грешную землю"
        turtle_stack = []
        key_list_re = "|".join(self.key_re_list)
        for values in re.finditer(r"(" + key_list_re + r"|.)", self.state):
            cmd = values.group(0)
            args = [float(x) for x in values.groups()[1:] if x]

            if 'F' in cmd:
                if len(args) > 0 and self.cmd_functions.get('F'):
                    self.cmd_functions['F'](t, self.length, *args)
                else:
                    self.t.fd(self.length)
            elif 'S' in cmd:
                if len(args) > 0 and self.cmd_functions.get('S'):
                    self.cmd_functions['S'](t, self.length, *args)
                else:
                    self.t.up()
                    self.t.forward(self.length)
                    self.t.down()
            elif '+' in cmd:
                if len(args) > 0 and self.cmd_functions.get('+'):
                    self.cmd_functions['+'](t, self.angle, *args)
                else:
                    self.t.left(self.angle)
            elif '-' in cmd:
                if len(args) > 0 and self.cmd_functions.get('-'):
                    self.cmd_functions['-'](t, self.angle, *args)
                else:
                    self.t.right(self.angle)
            elif 'A' in cmd:
                if self.cmd_functions.get('A'):
                    self.cmd_functions['A'](self.t, self.length, *args)
            elif "[" in cmd:
                turtle_stack.append((self.t.xcor(), self.t.ycor(), self.t.heading(), self.t.pensize()))
            elif "]" in cmd:
                xcor, ycor, head, w = turtle_stack.pop()
                self.set_turtle((xcor, ycor, head))
                self.width = w
                self.t.pensize(self.width)

        turtle.done()


width = 1200
height = 600
screen = turtle.Screen()
screen.setup(width, height, 0, 0)

t = turtle.Turtle()
t.ht()

axiom = "A"
pen_width = 2
f_len = 20
angle = 20

l_sys = LSystem2D(t, axiom, pen_width, f_len, angle)
l_sys.add_rules(("A", f"F(1, 1)[+({angle})A][-({angle})A]", 0.5),
                ("A", f"F(1, 1)[++({angle})A][+({angle})A][-({angle})A][--({angle})A]", 0.4),
                ("A", f"F(1, 1)[-({angle})A]", 0.05),
                ("A", f"F(1, 1)[+({angle})A]", 0.05),

                ("F(x, y)",
                 lambda x, y: f"F({(1.3 + random.triangular(-0.2, 0.2, random.gauss(0, 0.5))) * x}, {1.4 * y})"),
                ("+(x)", lambda x: f"+({x + random.triangular(-10, 10, random.gauss(0, 2))})"),
                ("-(x)", lambda x: f"-({x + random.triangular(-10, 10, random.gauss(0, 2))})"),
                )

l_sys.add_rules_move(("F", cmd_turtle_fd), ("+", cmd_turtle_left), ("-", cmd_turtle_right),
                     ("A", cmd_turtle_leaf))
l_sys.generate_path(7)
print(l_sys.state)
l_sys.draw_turtle((0, -200), 90)
