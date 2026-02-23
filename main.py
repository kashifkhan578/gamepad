import socket
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window
from plyer import accelerometer

Window.clearcolor = (0.05, 0.05, 0.08, 1) # Deep dark background

class ConnectionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(text="WIRELESS GAMEPAD", font_size=40, bold=True, color=(0.5, 0.8, 1, 1), size_hint_y=0.3)
        layout.add_widget(title)
        
        self.ip_input = TextInput(hint_text="Enter PC IP (e.g. 192.168.1.5)", font_size=30, size_hint_y=0.2, halign='center', background_color=(0.1, 0.1, 0.15, 1), foreground_color=(1, 1, 1, 1))
        layout.add_widget(self.ip_input)
        
        btn_connect = Button(text="CONNECT", font_size=30, bold=True, background_color=(0.2, 0.8, 0.4, 1), size_hint_y=0.2)
        btn_connect.bind(on_press=self.manual_connect)
        layout.add_widget(btn_connect)
        
        self.add_widget(layout)

    def manual_connect(self, instance):
        ip = self.ip_input.text.strip()
        if ip:
            controller_screen = self.manager.get_screen('controller')
            controller_screen.setup_network(ip, 5005)
            self.manager.current = 'controller'

class GameButton(Button):
    def __init__(self, btn_name, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.text = btn_name
        self.font_size = 24
        self.bold = True
        self.background_color = bg_color
        self.btn_name = btn_name

class ControllerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sock = None
        self.server_ip = ""
        self.server_port = 0
        self.sensor_enabled = False
        
        main_layout = BoxLayout(orientation='horizontal', padding=20, spacing=40)
        
        # LEFT SIDE: D-Pad & Sensor Info
        left_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.4)
        self.status_label = Label(text="Connected", color=(0, 1, 0, 1), size_hint_y=0.2)
        left_layout.add_widget(self.status_label)
        
        dpad_grid = GridLayout(cols=3, rows=3, spacing=5)
        dpad_grid.add_widget(Label())
        btn_up = GameButton("UP", (0.3, 0.3, 0.3, 1))
        btn_up.bind(state=self.on_btn_state)
        dpad_grid.add_widget(btn_up)
        dpad_grid.add_widget(Label())
        
        btn_left = GameButton("LEFT", (0.3, 0.3, 0.3, 1))
        btn_left.bind(state=self.on_btn_state)
        dpad_grid.add_widget(btn_left)
        dpad_grid.add_widget(Label(text="D-PAD", bold=True))
        btn_right = GameButton("RIGHT", (0.3, 0.3, 0.3, 1))
        btn_right.bind(state=self.on_btn_state)
        dpad_grid.add_widget(btn_right)
        
        dpad_grid.add_widget(Label())
        btn_down = GameButton("DOWN", (0.3, 0.3, 0.3, 1))
        btn_down.bind(state=self.on_btn_state)
        dpad_grid.add_widget(btn_down)
        dpad_grid.add_widget(Label())
        left_layout.add_widget(dpad_grid)
        main_layout.add_widget(left_layout)
        
        # RIGHT SIDE: Action Buttons (A, B, X, Y)
        right_layout = GridLayout(cols=2, rows=2, spacing=15, size_hint_x=0.4)
        btn_y = GameButton("Y", (1, 0.8, 0, 1)) # Yellow
        btn_y.bind(state=self.on_btn_state)
        right_layout.add_widget(btn_y)
        
        btn_x = GameButton("X", (0, 0.5, 1, 1)) # Blue
        btn_x.bind(state=self.on_btn_state)
        right_layout.add_widget(btn_x)
        
        btn_b = GameButton("B", (1, 0, 0, 1)) # Red
        btn_b.bind(state=self.on_btn_state)
        right_layout.add_widget(btn_b)
        
        btn_a = GameButton("A", (0, 1, 0, 1)) # Green
        btn_a.bind(state=self.on_btn_state)
        right_layout.add_widget(btn_a)
        
        action_container = BoxLayout(orientation='vertical', padding=[50, 50, 0, 50])
        action_container.add_widget(right_layout)
        main_layout.add_widget(action_container)
        
        self.add_widget(main_layout)

    def setup_network(self, ip, port):
        self.server_ip = ip
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            accelerometer.enable()
            self.sensor_enabled = True
            Clock.schedule_interval(self.read_sensors, 0.1)
        except Exception:
            pass

    def read_sensors(self, dt):
        if self.sensor_enabled:
            try:
                val = accelerometer.acceleration
                if val and len(val) >= 3:
                    x_axis = val[0]
                    if x_axis > 3.0:
                        self.send_command("LEFT", 1)
                        self.send_command("RIGHT", 0)
                    elif x_axis < -3.0:
                        self.send_command("RIGHT", 1)
                        self.send_command("LEFT", 0)
                    else:
                        self.send_command("LEFT", 0)
                        self.send_command("RIGHT", 0)
            except Exception:
                pass

    def on_btn_state(self, instance, value):
        state = 1 if value == "down" else 0
        self.send_command(instance.btn_name, state)

    def send_command(self, button, state):
        if not self.sock: return
        command = {"type": "button", "button": button, "state": state}
        try:
            self.sock.sendto(json.dumps(command).encode('utf-8'), (self.server_ip, self.server_port))
        except Exception:
            pass

class GamepadApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ConnectionScreen(name='connection'))
        sm.add_widget(ControllerScreen(name='controller'))
        return sm
    def on_stop(self):
        try: accelerometer.disable()
        except: pass

if __name__ == '__main__':
    GamepadApp().run()
