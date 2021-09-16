import logging
import logging.handlers
import sys

# import winrt.windows.ui.notifications as notifications
# import winrt.windows.data.xml.dom as dom


class PyNotify:
    lgr = logging.getLogger()
    lgr.setLevel(logging.INFO)
    # lgr.addHandler(logging.handlers.RotatingFileHandler('log.log'))

    def notify(self, AppID, title, text):
        """Send a Notification
        Keyword arguments:
        AppID -- Name of the APP
        title -- title of the notification
        text -- body of the notification
        """
        # this is a dummy method that should be replaced during init
        print('initializing seems to have failed')

    def __init__(self):
        if sys.platform == 'win32':
            from winrt.windows.ui.notifications import ToastNotificationManager
            from winrt.windows.ui.notifications import ToastNotification
            from winrt.windows.ui.notifications import ToastTemplateType

            def toast_notification(AppID, title, text):
                XML = ToastNotificationManager.get_template_content(
                    ToastTemplateType.TOAST_TEXT02
                )
                t = XML.get_elements_by_tag_name("text")
                t[0].append_child(XML.create_text_node(title))
                t[1].append_child(XML.create_text_node(text))
                notifier = ToastNotificationManager.create_toast_notifier(AppID)
                notifier.show(ToastNotification(XML))

            self.notify = toast_notification
        elif sys.platform == 'linux':
            import dbus

            def linux_notify(AppID, title, text):
                """Send a Notification
                Keyword arguments:
                AppID -- Name of the APP
                title -- title of the notification
                text -- body of the notification
                """
                bus_name = "org.freedesktop.Notifications"
                object_path = "/org/freedesktop/Notifications"
                interface = bus_name

                notify = dbus.Interface(
                    dbus.SessionBus().get_object(bus_name, object_path),
                    interface
                )

                notify.Notify(
                    AppID,       # app_name       (spec names)
                    0,       # replaces_id
                    '',     # app_icon
                    title,  # summary
                    text,  # body
                    '',  # actions
                    '',    # hints
                    -1,  # expire_timeout
                )
            self.notify = linux_notify
        else:
            print(f'The platform= {sys.platform} is not supported by pyNotify')
