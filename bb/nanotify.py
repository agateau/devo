import dbus

def notify(title, body, icon=""):
    try:
        bus = dbus.SessionBus()
    except dbus.exceptions.DBusException:
        return
    obj = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
    iface = dbus.Interface(obj, dbus_interface = 'org.freedesktop.Notifications')
    iface.Notify("nanotify",
        0,
        icon,
        title,
        body,
        [], # actions
        {}, # hints
        -1, # timeout       
        )

