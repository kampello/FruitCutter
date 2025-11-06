from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Line, Color, PushMatrix, PopMatrix, Rotate, Rectangle
from random import randint, uniform, choice
from kivy.core.window import Window
from kivy.uix.label import Label

Window.size = (600, 800)
tam = 100

class Fruit(Widget):
    def __init__(self, texture_source, **kwargs):
        super().__init__(**kwargs)
        self.size = (tam, tam)
        self.x = randint(50, Window.width - 100)
        self.y = 0
        self.velocity_x = uniform(-2, 2)
        self.velocity_y = randint(15, 25)
        self.gravity = -0.4
        self.angle = 0
        self.rotation_speed = uniform(-5, 5)

        with self.canvas:
            self.fruit_color = Color(1, 1, 1, 1)  # Color exclusiva
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
            self.rect = Rectangle(source=texture_source, pos=self.pos, size=self.size)
            PopMatrix()

        self.bind(pos=self.update_origin, size=self.update_origin)

    def update_origin(self, *args):
        self.rot.origin = self.center

    def move(self):
        self.velocity_y += self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.pos = (self.x, self.y)

        self.angle += self.rotation_speed
        self.rot.angle = self.angle
        self.rect.pos = self.pos

        if self.y + self.height < 0 and self.parent:
            self.parent.remove_widget(self)

class Splash(Widget):
    def __init__(self, texture_source='splash.png', **kwargs):
        super().__init__(**kwargs)
        self.texture_source = texture_source

        with self.canvas:
            self.color = Color(1, 1, 1, 1)  # Color exclusiva
            self.rect = Rectangle(source=self.texture_source, pos=self.pos, size=self.size)

        self.opacity = 1

        self.bind(pos=self.update_rect, size=self.update_rect)
        Clock.schedule_interval(self.fade_out, 1 / 60)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def fade_out(self, dt):
        self.opacity -= 0.01
        if self.opacity <= 0:
            if self.parent:
                self.parent.remove_widget(self)
            return False
        self.color.a = self.opacity
        return True


class SlicedFruit(Widget):
    def __init__(self, pos, texture_source, velocity, rotation_speed, **kwargs):
        super().__init__(**kwargs)
        self.size = (tam, tam)
        self.x, self.y = pos
        self.velocity_x, self.velocity_y = velocity
        self.rotation_speed = rotation_speed
        self.angle = 0

        with self.canvas:
            self.color = Color(1, 1, 1, 1)  # Color exclusiva para slice também
            PushMatrix()
            self.rot = Rotate(angle=self.angle, origin=self.center)
            self.img = Rectangle(source=texture_source, pos=self.pos, size=self.size)
            PopMatrix()

        Clock.schedule_interval(self.update, 1 / 60)

    def update(self, dt):
        self.velocity_y -= 0.4  # gravidade
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.angle += self.rotation_speed
        self.rot.angle = self.angle
        self.rot.origin = self.center
        self.pos = (self.x, self.y)
        self.img.pos = self.pos

        if self.y + self.height < 0:
            if self.parent:
                self.parent.remove_widget(self)

            Clock.unschedule(self.update)

class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.waste = 0
        self.score_label = Label(
            text=f"Score: {self.score}",
            font_size=32,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(200, 50),
            pos=(10, Window.height + 110)
        )
        self.add_widget(self.score_label)

        self.waste_label = Label(
            text=f"Waste: {self.waste}",
            font_size=32,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(200, 50),
            pos=(Window.width/2, Window.height + 110)
        )
        self.add_widget(self.waste_label)
        self.fruit_types = ['melancia', 'coco','laranja']

        with self.canvas.before:
            self.bg = Rectangle(source='fundo.png', pos=self.pos, size=Window.size)

        self.bind(size=self.update_bg, pos=self.update_bg)

        Clock.schedule_interval(self.update, 1 / 60)
        Clock.schedule_interval(self.spawn_fruit, 1.5)
        self.fruits = []

        self.trail_points = []
        self.max_trail_length = 20

    def spawn_fruit(self, dt):
        fruit_type = choice(self.fruit_types)
        fruit = Fruit(texture_source=f"{fruit_type}/fruit.png")
        fruit.meta = {
            'slash1': f"{fruit_type}/slash1.png",
            'slash2': f"{fruit_type}/slash2.png",
            'splash': f"{fruit_type}/splash.png"
        }
        self.add_widget(fruit)
        self.fruits.append(fruit)

    def update(self, dt):
        for fruit in self.fruits[:]:
            fruit.move()
            if fruit.y + fruit.height < 0:
                self.waste += 1
                self.waste_label.text = f"Waste: {self.waste}"
                self.remove_widget(fruit)
                self.fruits.remove(fruit)

        # Mantém o ponto atual mesmo sem movimento
        if self.trail_points and self._touch:
            last = self.trail_points[-1]
            self.trail_points.append(last)

        if self.trail_points:
            self.trail_points = self.trail_points[-self.max_trail_length:]
            self.draw_trail()

    def draw_trail(self):
        self.canvas.remove_group('trail')
        if len(self.trail_points) < 2:
            return

        with self.canvas:
            num_points = len(self.trail_points)
            for i in range(1, num_points):
                p1 = self.trail_points[i - 1]
                p2 = self.trail_points[i]

                # Opacidade e largura baseadas na idade do ponto (mais novos = mais fortes)
                alpha = i / num_points
                width = 2 + 6 * (1 - abs((i - num_points / 2) / (num_points / 2)))  # Mais grosso no meio

                Color(1, 1, 1, alpha, group='trail')  # Branco com fade
                Line(points=[*p1, *p2], width=width, cap='round', joint='round', group='trail')

    def on_touch_move(self, touch):
        self.trail_points.append((touch.x, touch.y))
        self.draw_trail()

        for fruit in self.fruits[:]:
            fx, fy = fruit.center
            dist = ((fx - touch.x) ** 2 + (fy - touch.y) ** 2) ** 0.5
            if dist < tam:
                self.remove_widget(fruit)
                self.fruits.remove(fruit)
                self.score += 1
                self.score_label.text = f"Score: {self.score}"

                part1 = SlicedFruit(
                    pos=fruit.pos,
                    texture_source=fruit.meta['slash1'],
                    velocity=(-3, 10),
                    rotation_speed=-5
                )
                part2 = SlicedFruit(
                    pos=fruit.pos,
                    texture_source=fruit.meta['slash2'],
                    velocity=(3, 10),
                    rotation_speed=5
                )
                self.add_widget(part1)
                self.add_widget(part2)

                fx, fy = fruit.center
                splash = Splash(
                    pos=(fx - tam / 2, fy - tam / 2),
                    size=(tam, tam),
                    texture_source=fruit.meta['splash']
                )
                self.add_widget(splash)

    def on_touch_up(self, touch):
        self._touch = None
        self.trail_points.clear()
        self.canvas.remove_group('trail')

    def on_touch_down(self, touch):
        self._touch = touch
        self.trail_points.append((touch.x, touch.y))
        self.draw_trail()

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

class FruitNinjaApp(App):
    def build(self):
        return Game()

if __name__ == '__main__':
    FruitNinjaApp().run()
