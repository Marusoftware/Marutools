Addon API Reference
===================
Addon API has some useful API.

.. py:class:: AddonAPI

    .. py:attribute:: name
        :type: str
        
        Addon Name

    .. py:attribute:: logger
        :type: Logger
        :canonical: libtools.core.Logger

        Logger object for addon

    .. py:attribute:: appinfo
        :type: dict

        Marutools runtime infomation
    
    .. py:attribute:: ext
        :type: str

        Open file extention
    
    .. py:attribute:: ui
        :type: UI
        :canonical: libtools.addon.UI

        UI controler
    
    .. py:attribute:: app 
        :type: Core

        Marutools Core
    
    .. py:attribute:: saved
        :type: bool

        Flag for is saved file.

==
UI
==

UI controling class

.. py:class:: UI

    .. py:attribute:: parent

        Parent UI object. If not having, it is `None`.
    
    .. py:attribute:: type
        :type: str

        | UI object type. UI object is showing Frame widget or window.
        | ``main``: Main window
        | ``frame``: Frame widget
        | ``dialog``: Dialog widget(like Warning window...)
        | ``sub``: Sub window
    
    .. py:attribute:: backend
        :type: str

        | Backend name.
        | ``tkinter``:tkinter GUI library
    
    .. py:classmethod:: changeTitle(title)

        Change window title.

        .. warning:: 
            This works successfully only when UI object type is ``main`` or ``sub``

        :param str title: Title to set.

    .. py:classmethod:: changeIcon(icon_path)

        Change window icon(it's on title bar and task bar).

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``
        
        :param str title: Icon file path to set.

    .. py:classmethod:: fullscreen(tf=None):

        Change window to fullscreen.

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``

        :param bool tf: True to fullscreen. False to fullscreen. default(None) to nomal size.
    
    .. py:classmethod:: changeSize(size):

        Change window size.

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``

        :param str size: ``{width}x{height}+{x}+{y}``
    
    .. py:classmethod:: uisetting(frame, txt):

        The widget for UI setting.

        :param libtools.Frame frame: Frame to show settings.
        :param Lang txt: l10n text in dict like object

    .. py:classmethod:: setcallback(name, callback)

        Set callback.

        :param str name: | Callback name.
                         | ``close``: Fire on close window.
                         | ``macos_help``: Click help menu button on Macos
                         | ``macos_settngs``:Click settings menu button on Macos
        :param callable callback: Callback function.

    .. py:classmethod:: makeSubwindow(dialog=False, **options)

        Make Subwindow

        :param bool dialog: Dialog mode.

======
Logger
======

Now writing.....

.. py:class:: Logger
