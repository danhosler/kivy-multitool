from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivymd.bottomsheet import MDListBottomSheet, MDGridBottomSheet
from kivymd.button import MDIconButton
from kivymd.date_picker import MDDatePicker
from kivymd.dialog import MDDialog
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.material_resources import DEVICE_TYPE
from kivymd.selectioncontrols import MDCheckbox
from kivymd.theming import ThemeManager
from kivymd.time_picker import MDTimePicker
from kivymd.tabs import MDTab
from kivy.clock import Clock, mainthread
from kivymd.list import TwoLineListItem, OneLineListItem, ThreeLineListItem, MDList
from kivymd.button import MDRaisedButton
from kivymd.navigationdrawer import NavigationDrawerIconButton
from kivy.properties import (StringProperty, NumericProperty, ObjectProperty, ListProperty)
from kivy.factory import Factory


import threading
import requests
from functools import partial
import time
from collections import deque


palette_q = deque(['Red', 'BlueGrey', 'Amber', 'DeepPurple', 'Blue', 'DeepOrange', 'Yellow', 'Cyan', 'Purple', 'Green',])
tab_count = 0


def loading(a_func):
    def wrapTheFunction(self, *args):
        Clock.schedule_once(self.loading_screen.show_loading)
        a_func(self)
        Clock.schedule_once(self.loading_screen.hide_loading)

    return wrapTheFunction


class ScreenWorker(Screen):
    def __init__(self, loading_screen=None, **kwargs):
        super(ScreenWorker, self).__init__(**kwargs)
        self.loading_screen = self
        self.app = App.get_running_app()
        threading.Thread(target=self.fetch_screen).start()
        self.my_widgets = {}
        self.widget_count = 0

    def show_loading(self, *args):
        self.ids.scr_mngr_mode.current = "progress"

    def hide_loading(self, *args):
        self.ids.scr_mngr_mode.current = "work"


    @loading
    def fetch_screen(self):
        count = 0
        retries = 10
        while True:
            try:
                r = requests.get(self.app.host+'/'+self.name)
            except Exception as e:
                time.sleep(1)
                count+=1
                if count > retries:
                    raise
            else:
                break
        hey = r.json()
        time.sleep(1)
        Clock.schedule_once(partial(self.paint_screen, self.ids.scroll_worker, hey))

    def paint_screen(self, root, data, *args):
        for widget in data:
            self.widget_count += 1
            widgets = widget.pop("widgets", None)
            release = widget.pop("on_release", None)
            size = widget.pop("size", None)
            left_action_items = widget.pop("left_action_items", None)
            id = widget.pop("id", str(self.widget_count))
            foo = Factory.get(widget.pop('type'))(**widget)
            foo.id = id
            if left_action_items is not None:
                items = ListProperty()
                for item in left_action_items:
                    if item[1] == "lambda x: None":
                        items = [[item[0], lambda x: None]]
                    else:
                        items = [[item[0], item[1]]]
                foo.left_action_items = items
            if size is not None and size == "root.size":
                foo.size = root.size
            if release is not None:
                foo.bind(on_release=partial(self.callback, **release))
            self.my_widgets[foo.id] = foo
            root.add_widget(foo)
            if widgets is not None:
                self.paint_screen(foo, widgets)


    def callback(self, *args, **kwargs):
        params = {}
        for name, widget in self.my_widgets.items():
            try:
                params[name] = widget.text
            except Exception:
                pass

        r = requests.get(self.app.host + '/' + kwargs["api"], params=params)
        hey = r.json()
        for id in hey["text"]:
            self.my_widgets[id].text = hey["text"][id]

class NavigationDrawerIconButtdon(NavigationDrawerIconButton):
    pass


class NumPad(BoxLayout):
    display_text = StringProperty("0")
    display_value = NumericProperty(0)
    init_value = NumericProperty(100)
    maximum_value = NumericProperty(None, allownone=True)
    minimum_value = NumericProperty(None, allownone=True)
    return_callback = ObjectProperty(None, allownone=True)
    units = StringProperty(None, allownone=True)

    def __init__(self, p=None, **kwargs):
        super(NumPad, self).__init__(**kwargs)
        self.p = p
        self.app = App.get_running_app()

    def check_minimum_value(self):
        if self.minimum_value != None:
            if self.display_value < self.minimum_value:
                self.display_text = str(self.minimum_value)

    def button_callback(self, button_str):
        if button_str == "Find":

            self.p.process_button_click(self.display_text)

        if button_str in [str(x) for x in range(10)]:
            if self.display_text == '0':
                self.display_text = button_str
            else:
                self.display_text = self.display_text + button_str
            maximum_value = self.maximum_value
            if maximum_value != None:
                if self.display_value > maximum_value:
                    self.display_value = maximum_value
        elif button_str == 'del':
            self.display_text = self.display_text[:-1]
        elif button_str == 'ret':
            self.check_minimum_value()
            self.return_callback(self.display_value, True)

    def on_display_text(self, instance, value):
        if value == '':
            self.display_text = '0'
            return
        if self.maximum_value != None and int(value) > self.maximum_value:
            self.display_text = str(self.maximum_value)
            return
        self.display_value = int(value)
        if self.return_callback is not None:
            self.return_callback(self.display_value, False)


class TabWorker(MDTab):
    global palette_q
    global tab_count

    def __init__(self, **kwargs):
        super(TabWorker, self).__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self.populate_nav)
        self.screens = {}
        self.loading_screen = self

    def callback(self, event, x):
        if x in self.screens:
            self.ids.scr_mngr.current = x
        else:
            foo = ScreenWorker(loading_screen=self, name=x)
            self.screens[x] = foo
            self.ids.scr_mngr.add_widget(foo)
            self.ids.scr_mngr.current = x

    def show_loading(self, *args):
        self.ids.scr_mngr_mode.current = "progress"

    def hide_loading(self, *args):
        self.ids.scr_mngr_mode.current = "work"

    def populate_nav(self, *args):
        threading.Thread(target=self.fetch_nav).start()

    @loading
    def fetch_nav(self):
        count = 0
        retries = 10
        while True:
            try:
                if self.name == "new":
                    r = requests.get(self.app.host+'/getnav')
                else:
                    r = requests.get(self.app.host+'/getworknav')
            except Exception as e:
                time.sleep(1)
                count+=1
                if count > retries:
                    raise
            else:
                break
        hey = r.json()
        Clock.schedule_once(partial(self.paint_nav, hey))

    def paint_nav(self, hey, *args):
        for thing in hey:
            ic = NavigationDrawerIconButton()
            p = partial(self.callback)
            ic.bind(on_release=partial(self.callback, x=hey[thing]))
            ic.text = thing
            self.ids.nav_drawer.add_widget(ic)
        self.ids.box1.add_widget(NumPad(p=self))

    def process_button_click(self, displaytext):
        global tab_count
        tab_count += 1
        newTab = TabWorker(name=str(tab_count), text=displaytext)
        self.parent_widget.add_widget(newTab)
        newPalette = palette_q.popleft()
        palette_q.append(newPalette)
        newTab.palette = newPalette
        newTab.on_tab_press()

    def on_tab_press(self, *args):
        par = self.parent_widget
        if par.previous_tab is not self:
            if par.previous_tab.index > self.index:
                par.ids.tab_manager.transition.direction = "right"
            elif par.previous_tab.index < self.index:
                par.ids.tab_manager.transition.direction = "left"
            par.ids.tab_manager.current = self.name
            par.previous_tab = self
            app = App.get_running_app()
            if self.name == "new":
                app.theme_cls.theme_style = 'Light'
                app.theme_cls.primary_palette = 'Blue'
            else:
                app.theme_cls.theme_style = 'Dark'
                app.theme_cls.primary_palette = self.palette


class RootWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.stop = threading.Event()

    def change_screen(self, screen):
        if self.ids.tab_panel.previous_tab.name != "new":
            self.ids.tab_panel.previous_tab.ids.scr_mngr.current = screen


class MultiToolApp(App):
    theme_cls = ThemeManager()
    title = "MultiTool"
    host = "http://10.0.0.15:5000"
    def on_stop(self):
        # The Kivy event loop is about to stop, set a stop signal;
        # otherwise the app window will close, but the Python process will
        # keep running until all secondary threads exit.
        self.root.stop.set()

    def build(self):
        count = 0
        retries = 10
        while True:
            try:
                r = requests.get(self.host+'/getkvfile')
            except:
                try:
                    r = requests.get('http://127.0.0.1:5000/getkvfile')
                except Exception:
                    time.sleep(1)
                    count += 1
                    if count > retries:
                        raise
                else:
                    break
            else:
                break
        self.root = Builder.load_string(r.text)
        return self.root

    def on_pause(self):
        return True