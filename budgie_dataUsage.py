import gi.repository

gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, Gio
import os
import subprocess
import json
import datatools as clt

"""
Budgie ShowDataUsage
Author: TJ Thornsberry
"""

css_data = """
.colorbutton {
  border-color: transparent;
  background-color: hexcolor;
  padding: 0px;
  border-width: 1px;
  border-radius: 4px;
}
.colorbutton:hover {
  border-color: hexcolor;
  background-color: hexcolor;
  padding: 0px;
  border-width: 1px;
  border-radius: 4px;
}
"""

colorpicker = os.path.join(clt.app_path, "colorpicker")


class BudgieShowData(GObject.GObject, Budgie.Plugin):
    """ This is simply an entry point into your Budgie Applet implementation.
        Note you must always override Object, and implement Plugin.
    """

    __gtype_name__ = "BudgieShowData"

    def __init__(self):
        """ Initialisation is important.
        """
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        """ This is where the real fun happens. Return a new Budgie.Applet
            instance with the given UUID. The UUID is determined by the
            BudgiePanelManager, and is used for lifetime tracking.
        """
        return BudgieShowDataApplet(uuid)


class BudgieShowDataSettings(Gtk.Grid):
    def __init__(self, setting):

        super().__init__()
        self.setting = setting
        self.set_row_homogeneous = True
        self.set_column_homogeneous = True

        # files & colors
        self.mute_yesterday = not clt.config["MUTE"].getboolean("yesterday")
        self.mute_today = not clt.config["MUTE"].getboolean("today")
        self.mute_week = not clt.config["MUTE"].getboolean("week")
        self.mute_month = not clt.config["MUTE"].getboolean("month")
        self.mute_shadow = not clt.config["MUTE"].getboolean("shadow")
        # grid & layout
        self.set_row_spacing(12)
        element_h_sizer1 = self.h_spacer(6)
        self.attach(element_h_sizer1, 0, 0, 1, 7)
        element_h_sizer2 = self.h_spacer(6)
        self.attach(element_h_sizer2, 2, 0, 1, 7)
        element_h_sizer3 = self.h_spacer(6)
        self.attach(element_h_sizer3, 4, 0, 1, 7)
        element_h_sizer4 = self.h_spacer(6)
        self.attach(element_h_sizer4, 6, 0, 1, 7)
        # Initialize UI Items
        # -Boxes (Containers)
        self.box_combobox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box_yesterday = Gtk.Box()
        self.box_today = Gtk.Box()
        self.box_week = Gtk.Box()
        self.box_month = Gtk.Box()
        self.box_shadow = Gtk.Box()
        self.box_position = Gtk.Box()
        # -Buttons
        self.y_color = Gtk.Button()
        self.t_color = Gtk.Button()
        self.w_color = Gtk.Button()
        self.m_color = Gtk.Button()
        self.shadow_color = Gtk.Button()
        self.apply = Gtk.Button("OK")
        # -Checkboxes
        self.display_yesterday = Gtk.CheckButton(" Show Yesterday")
        self.display_today = Gtk.CheckButton(" Show Today")
        self.display_week = Gtk.CheckButton(" Show Week")
        self.display_month = Gtk.CheckButton(" Show Month")
        self.display_shadow = Gtk.CheckButton(" Add Shadow (Readability)")
        self.set_pos_button = Gtk.CheckButton("Set custom position (px)")
        # -ComboBoxes
        self.interface_combo = self.setup_interfaces()
        self.display_combo = self.setup_display_type()
        # -Labels
        interface_label = Gtk.Label(" Interface:")
        display_label = Gtk.Label(" Display Type:")
        yesterday_label = Gtk.Label("    Set Yesterday's color")
        today_label = Gtk.Label("    Set Today's color")
        week_label = Gtk.Label("    Set color for Week")
        month_label = Gtk.Label("    Set color for Month")
        shadow_label = Gtk.Label("    Set shadow's color")
        self.xpos_label = Gtk.Label("x: ")
        self.ypos_label = Gtk.Label("  y: ")
        spacer1 = Gtk.Label("")
        spacer2 = Gtk.Label("")
        footnote_1 = Gtk.Label("Applet runs without a panel icon.")
        footnote_2 = Gtk.Label("Make sure to properly set up vnstat before using this.")
        # -Entries
        self.x_pos = Gtk.Entry()
        self.y_pos = Gtk.Entry()
        self.x_pos.set_width_chars(4)
        self.y_pos.set_width_chars(4)
        # attach to grid
        self.box_combobox.pack_start(interface_label, False, False, 0)
        self.box_combobox.pack_start(self.interface_combo, False, False, 0)
        self.box_combobox.pack_start(display_label, False, False, 0)
        self.box_combobox.pack_start(self.display_combo, False, False, 0)
        self.box_yesterday.pack_start(self.y_color, False, False, 0)
        self.box_yesterday.pack_start(yesterday_label, False, False, 0)
        self.box_today.pack_start(self.t_color, False, False, 0)
        self.box_today.pack_start(today_label, False, False, 0)
        self.box_week.pack_start(self.w_color, False, False, 0)
        self.box_week.pack_start(week_label, False, False, 0)
        self.box_month.pack_start(self.m_color, False, False, 0)
        self.box_month.pack_start(month_label, False, False, 0)
        self.box_shadow.pack_start(self.shadow_color, False, False, 0)
        self.box_shadow.pack_start(shadow_label, False, False, 0)
        self.attach(self.box_combobox, 1, 1, 1, 1)
        self.attach(self.display_yesterday, 1, 2, 1, 1)
        self.attach(self.display_today, 1, 3, 1, 1)
        self.attach(self.display_week, 1, 4, 1, 1)
        self.attach(self.display_month, 1, 5, 1, 1)
        self.attach(self.display_shadow, 1, 6, 1, 1)
        self.attach(self.box_yesterday, 1, 7, 1, 1)
        self.attach(self.box_today, 1, 8, 1, 1)
        self.attach(self.box_week, 1, 9, 1, 1)
        self.attach(self.box_month, 1, 10, 1, 1)
        self.attach(self.box_shadow, 1, 11, 1, 1)
        self.attach(spacer1, 1, 12, 1, 1)
        self.attach(self.set_pos_button, 1, 13, 1, 1)
        self.attach(self.box_position, 1, 14, 1, 1)
        self.attach(spacer2, 1, 15, 1, 1)
        self.attach(footnote_2, 1, 16, 1, 1)
        self.attach(footnote_1, 1, 17, 1, 1)
        # Finish setting up things up
        self.setup_color_buttons()
        self.setup_position_selection()
        # set initial states
        self.display_yesterday.set_active(self.mute_yesterday)
        self.display_today.set_active(self.mute_today)
        self.display_week.set_active(self.mute_week)
        self.display_month.set_active(self.mute_month)
        self.display_shadow.set_active(self.mute_shadow)
        self.set_yesterday_state(self.mute_yesterday)
        self.set_today_state(self.mute_today)
        self.set_week_state(self.mute_week)
        self.set_month_state(self.mute_month)
        self.set_shadow_state(self.mute_shadow)
        self.display_yesterday.connect("toggled", self.toggle_show, "yesterday")
        self.display_today.connect("toggled", self.toggle_show, "today")
        self.display_week.connect("toggled", self.toggle_show, "week")
        self.display_month.connect("toggled", self.toggle_show, "month")
        self.display_shadow.connect("toggled", self.toggle_show, "shadow")
        self.interface_combo.connect("changed", self.change_interface)
        self.display_combo.connect("changed", self.change_display)
        # color buttons & labels
        self.set_pos_button.connect("toggled", self.toggle_cuspos)
        self.apply.connect("clicked", self.get_xy)
        self.update_color()
        self.show_all()

    @staticmethod
    def setup_interfaces():
        interface_options = Gtk.ListStore(str)
        interfaces = clt.get_interfaces()
        for item in interfaces:
            interface_options.append([item])
        interface_combo = Gtk.ComboBox.new_with_model(interface_options)
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("xalign", 0.51)
        interface_combo.pack_start(renderer_text, True)
        interface_combo.add_attribute(renderer_text, "text", 0)
        idx = interfaces.index(clt.config["GENERAL"]["interface"])
        interface_combo.set_active(idx)
        return interface_combo

    @staticmethod
    def setup_display_type():
        display_options = Gtk.ListStore(str)
        for item in ["Short", "Long", "Detailed", "Minimal"]:
            display_options.append([item])
        display_combo = Gtk.ComboBox.new_with_model(display_options)
        renderer_text = Gtk.CellRendererText()
        renderer_text.set_property("xalign", 0.51)
        display_combo.pack_start(renderer_text, True)
        display_combo.add_attribute(renderer_text, "text", 0)
        display_combo.set_active(int(clt.config["GENERAL"]["display"]))
        return display_combo

    def setup_color_buttons(self):
        color_order = ["yesterday", "today", "week", "month", "shadow"]
        color_buttons = [self.y_color, self.t_color, self.w_color, self.m_color, self.shadow_color]
        for i, x in enumerate(color_buttons):
            x.connect("clicked", self.pick_color, color_order[i])
            x.set_size_request(10, 10)

    def setup_position_selection(self):
        for item in [
            self.xpos_label, self.x_pos, self.ypos_label, self.y_pos,
        ]:
            self.box_position.pack_start(item, False, False, 0)
        self.box_position.pack_end(self.apply, False, False, 0)
        self.set_initial_pos_state()

    @staticmethod
    def change_interface(combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            text = model[tree_iter][0]
            clt.config["GENERAL"]["interface"] = text
            with open(clt.config_file, 'w') as cf:
                clt.config.write(cf)
        clt.restart_data()

    @staticmethod
    def change_display(combo):
        tree_iter = combo.get_active_iter()
        if tree_iter is not None:
            model = combo.get_model()
            text = model[tree_iter][0]
            idx = ["Short", "Long", "Detailed", "Minimal"].index(text)
            clt.config["GENERAL"]["display"] = str(idx)
            with open(clt.config_file, 'w') as cf:
                clt.config.write(cf)
        clt.restart_data()

    def set_yesterday_state(self, val=None):
        self.mute_yesterday = not clt.config["MUTE"].getboolean("yesterday")
        val = val if val else self.mute_yesterday
        for item in [self.box_yesterday, self.y_color]:
            item.set_sensitive(val)

    def set_today_state(self, val=None):
        self.mute_today = not clt.config["MUTE"].getboolean("today")
        val = val if val else self.mute_today
        for item in [self.box_today, self.t_color]:
            item.set_sensitive(val)

    def set_week_state(self, val=None):
        self.mute_week = not clt.config["MUTE"].getboolean("week")
        val = val if val else self.mute_week
        for item in [self.box_week, self.w_color]:
            item.set_sensitive(val)

    def set_month_state(self, val=None):
        self.mute_month = not clt.config["MUTE"].getboolean("month")
        val = val if val else self.mute_month
        for item in [self.box_month, self.m_color]:
            item.set_sensitive(val)

    def set_shadow_state(self, val=None):
        self.mute_shadow = not clt.config["MUTE"].getboolean("shadow")
        val = val if val else self.mute_shadow
        for item in [self.box_shadow, self.shadow_color]:
            item.set_sensitive(val)

    def set_initial_pos_state(self):
        # set initial state of items in the custom position section
        state_data = clt.get_textposition()
        state = state_data[0]
        if state:
            self.x_pos.set_text(str(state_data[1]))
            self.y_pos.set_text(str(state_data[2]))
        for items in [
            self.y_pos, self.x_pos, self.apply, self.xpos_label, self.ypos_label
        ]:
            items.set_sensitive(state)
        self.set_pos_button.set_active(state)

    def get_xy(self, button):
        x = self.x_pos.get_text()
        y = self.y_pos.get_text()
        # check for correct input
        try:
            new_pos = [str(int(p)) for p in [x, y]]
            clt.config["GENERAL"]["position"] = ",".join(new_pos)
            with open(clt.config_file, 'w') as cf:
                clt.config.write(cf)
        except (FileNotFoundError, ValueError, IndexError):
            pass
        clt.restart_data()

    def toggle_cuspos(self, button):
        new_state = button.get_active()
        for widget in [
            self.y_pos, self.x_pos, self.xpos_label, self.ypos_label, self.apply
        ]:
            widget.set_sensitive(new_state)
        if new_state is False:
            self.x_pos.set_text("")
            self.y_pos.set_text("")
            clt.config["GENERAL"]["position"] = ",".join(["900", "50"])
            clt.config["GENERAL"]["custom_position"] = "False"
            with open(clt.config_file, 'w') as cf:
                clt.config.write(cf)
            clt.restart_data()
        else:
            clt.config["GENERAL"]["custom_position"] = "True"
            with open(clt.config_file, 'w') as cf:
                clt.config.write(cf)

    @staticmethod
    def h_spacer(added_width):
        # horizontal spacer
        space_grid = Gtk.Grid()
        if added_width:
            label1 = Gtk.Label()
            label2 = Gtk.Label()
            space_grid.attach(label1, 0, 0, 1, 1)
            space_grid.attach(label2, 1, 0, 1, 1)
            space_grid.set_column_spacing(added_width)
        return space_grid

    def toggle_show(self, button, option):
        self.mute_yesterday = not clt.config["MUTE"].getboolean("yesterday")
        self.mute_today = not clt.config["MUTE"].getboolean("today")
        self.mute_week = not clt.config["MUTE"].getboolean("week")
        self.mute_month = not clt.config["MUTE"].getboolean("month")
        self.mute_shadow = not clt.config["MUTE"].getboolean("shadow")
        new_state = not button.get_active()
        clt.config["MUTE"][option] = str(new_state)
        with open(clt.config_file, 'w') as cf:
            clt.config.write(cf)
        try:
            if option == "yesterday":
                self.set_yesterday_state()
            elif option == "today":
                self.set_today_state()
            elif option == "week":
                self.set_week_state()
            elif option == "month":
                self.set_month_state()
            elif option == "shadow":
                self.set_shadow_state()
        except UnboundLocalError:
            pass
        clt.restart_data()

    @staticmethod
    def set_css(hex_color):
        provider = Gtk.CssProvider.new()
        provider.load_from_data(
            css_data.replace("hexcolor", hex_color).encode()
        )
        return provider

    def color_button(self, button, hex_color):
        provider = self.set_css(hex_color)
        color_cont = button.get_style_context()
        color_cont.add_class("colorbutton")
        Gtk.StyleContext.add_provider(
            color_cont,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def update_color(self, *args):
        with open(clt.config_file) as cf:
            clt.config.read_file(cf)
        yesterday_color = clt.hexcolor(clt.config["COLORS"]["yesterday"])
        today_color = clt.hexcolor(clt.config["COLORS"]["today"])
        week_color = clt.hexcolor(clt.config["COLORS"]["week"])
        month_color = clt.hexcolor(clt.config["COLORS"]["month"])
        shadow_color = clt.hexcolor(clt.config["COLORS"]["shadow"])
        self.color_button(self.y_color, yesterday_color)
        self.color_button(self.t_color, today_color)
        self.color_button(self.w_color, week_color)
        self.color_button(self.m_color, month_color)
        self.color_button(self.shadow_color, shadow_color)

    def pick_color(self, button, f):
        w_data = clt.get(["wmctrl", "-l"])
        if "ShowData - set color" not in w_data:
            color_picker_subprocess = Gio.Subprocess.new([colorpicker, f], 0)
            color_picker_subprocess.wait_check_async(None, self.update_color)
            self.update_color()


class BudgieShowDataApplet(Budgie.Applet):
    """ Budgie.Applet is in fact a Gtk.Bin """

    def __init__(self, uuid):
        Budgie.Applet.__init__(self)
        self.uuid = uuid
        clt.restart_data()

    def do_get_settings_ui(self):
        """Return the applet settings with given uuid"""
        return BudgieShowDataSettings(self.get_applet_settings(self.uuid))

    def do_supports_settings(self):
        """Return True if support setting through Budgie Setting,
        False otherwise.
        """
        return True
