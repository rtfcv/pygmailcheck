import logging
import logging.handlers
import sys

# import winrt.windows.ui.notifications as notifications
# import winrt.windows.data.xml.dom as dom


class PyNotify:
    lgr = logging.getLogger()
    lgr.setLevel(logging.INFO)
    # lgr.addHandler(logging.handlers.RotatingFileHandler('log.log'))

    notify = None

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
        else:
            print(sys.platform)
