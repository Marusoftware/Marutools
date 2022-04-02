Addon API Reference
===================
Addon API has some useful API.

.. class:: AddonAPI

    :canonical: libtools.addon.AddonAPI

    .. attribute:: name
        :type: str
        
        Addon Name

    .. attribute:: logger
        :type: Logger
        :canonical: libtools.core.Logger

        Logger object for addon

    .. attribute:: appinfo
        :type: dict

        Marutools runtime infomation
    
    .. attribute:: ext
        :type: str

        Open file extention
    
    .. attribute:: ui
        :type: UI
        :canonical: libtools.addon.UI

        UI controler
    
    .. attribute:: app 
        :type: Core

        Marutools Core
    
    .. attribute:: saved
        :type: bool

        Flag for is saved file.

==
UI
==

UI controling classes

.. py:class:: UI

    .. attribute:: parent

        Parent UI object. If not having, it is `None`.
    
    .. attribute:: type
        :type: str

        | UI object type. UI object is showing Frame widget or window.
        | ``main``: Main window
        | ``frame``: Frame widget
        | ``dialog``: Dialog widget(like Warning window...)
        | ``sub``: Sub window
    
    .. attribute:: backend
        :type: str

        | Backend name.
        | ``tkinter``:tkinter GUI library
    
    .. method:: changeTitle(title)

        Change window title.

        .. warning:: 
            This works successfully only when UI object type is ``main`` or ``sub``

        :param str title: Title to set.

    .. method:: changeIcon(icon_path)

        Change window icon(it's on title bar and task bar).

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``
        
        :param str title: Icon file path to set.

    .. method:: fullscreen(tf=None)

        Change window to fullscreen.

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``

        :param bool tf: True to fullscreen. False to fullscreen. default(None) to nomal size.
    
    .. method:: changeSize(size):

        Change window size.

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``

        :param str size: ``{width}x{height}+{x}+{y}``
    
    .. method:: uisetting(frame, txt)

        The widget for UI setting.

        :param libtools.Frame frame: Frame to show settings.
        :param Lang txt: l10n text in dict like object

    .. method:: setcallback(name, callback)

        Set callback.

        :param str name: | Callback name.
                         | ``close``: Fire on close window.
                         | ``macos_help``: Click help menu button on Macos
                         | ``macos_settings``:Click settings menu button on Macos
        :param callable callback: Callback function.

    .. method:: makeSubwindow(dialog=False, **options)

        Make Subwindow

        :param bool dialog: Dialog mode.
    
    .. method:: close()

        Close window/frame.
    
    .. method:: wait()

        Wait until close window.

        .. warning::
            This works successfully only when UI object type is ``main`` or ``sub``
    
    .. method:: exist()

        Return whether the window/frame is open.

        :return: whether the window/frame is open.
        :rtype: bool

    .. method:: mainloop()

        Window Mainloop.

        .. warning::
            This works successfully only when UI object type is ``main``.
            And also, must NOT BE run twice or above.

    .. method:: Frame()
        
        Frame widget.

        :return: Frame widget object
        :rtype: UI
    
    .. method:: Label(label=None)

        Label widget.

        :param str label: Label text
        :return: Label widget object
        :rtype: WidgetBase
    
    .. method:: Image(image=None)
        
        Image widget.

        :return: Image widget object
        :rtype: WidgetBase
    
    .. method:: Menu()

        Menu widget.

        :return: Menu widget object
        :rtype: Menu
    
    .. method:: Notebook()

        Notebook widget.

        :return: Notebook widget object
        :rtype: Notebook
    
    .. attribute:: Dialog
        :type: Dialog
    
    .. attribute:: Input
        :type: Input

.. class:: Dialog
    
    .. method:: askfile(multi=False, save=False)

        Ask filepath Dialog.

        :param bool multi: Multi selection enable/disable
        :param bool save: Save filepath(``True``) or Open filepath(``False``)
        :return: Filepath
        :rtype: str or None
    
    .. method:: askdir()

        Ask directory(folder) path Dialog.

        :return: Directory path
        :rtype: str
     
    .. method:: error()
        
        Show error Dialog.

    .. method:: info()

        Show infomation Dialog.
    
    .. method:: warn()

        Show warning Dialog.

    .. method:: question(type, title, message)

        Asking Dialog.

        :param str type: | Ask type.
                         | ``okcancel``: select "ok"(return ``True``) or "cancel"(return ``False``)
                         | ``retrycancel``: select "retry"(``True``) or "cancel"(``False``)
                         | ``yesno``: select "yes"(``True``) or "no"(``False``)
                         | ``yesnocancel``: select "yes"(``True``) or "no"(``False``) or "cancel"(``None``)
                         | ``text``: Input text. If cancel, return ``None``
        :param str title: Dialog title
        :param str message: Dialog message
        :return: Selected (or Inputed) value.
        :rtype: bool or str or None

.. class:: Input

    .. method:: Button(label="", command=None)

        Button widget.

        :param str label: Button label.
        :param callable command: Button on-clicking callback
        :return: Button widget object
        :rtype: Button

    .. method:: List

        List widget.

        :return: List widget object
        :rtype: List
    
    .. method:: Form(type="text", command=None)

        Text inputting widget.(just one line)

        :param str type: | Form type.
                         | ``text``: Normal plain text input.
                         | ``password``: Password input.
                         | ``filesave``: Save file asking.
                         | ``fileopen``: Open file asking.
                         | ``fileopenmulti``: Open file asking (multiple).
                         | ``filesavemulti``: Save file asking (multiple).
        :param callable command: Form on-changing callback
        :return: Form widget object.
        :rtype: Form

    .. method:: Text(scroll=True, command=None)

        Text inputting widget.(multi line)

        :param bool scroll: Scrollbar
        :param callable command: Text on-changing callback
        :param bool readonly: Readonly
        :return: Text widget object
        :rtype: Text
    
    .. method:: CheckButton(label=None, command=None, default=False)

        Check button widget.

        :param str label: Button label.
        :param callable command: CheckButton on-clicking callback
        :param bool default: Default value.
        :return: CheckButton widget object
        :rtype: CheckButton
    
    .. method:: Select(default="", command=None, values=[], inline=False, label="")

        Select widget.

        :param str default: Default value
        :param callable command: on-selecting callback
        :param List[str] values: Values to select
        :param bool inline: Inline mode
        :param str label: Select label(on left)
        :return: Select widget object
        :rtype: Select

======
Logger
======

Now writing.....

.. py:class:: Logger
