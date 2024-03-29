Document for Developer
======================
This is guide for developer.

============
Introduction
============
First, Marutools has addon system.
You can make addon in very easy steps.

========
Tutorial
========
Here comes addon making tutorial.

Get started
-----------
First, you have to decide that it is big addon or small addon.
Big addon is consisted with folder(it's same as python package).
Small addon is consisted with only one python script.
It can change later, but it may be hard.

Now, Marutools contain only Marueditor.
So, you can make addon only for editor.

This is base code:

.. literalinclude:: _static/addon_base.py
    :language: python
    :linenos:
    :encoding: utf-8

:download:`addon_base.py <_static/addon_base.py>`

.. class:: Edit

    .. attribute:: name
        :type: str
        
        Addon name.
    
    .. attribute:: description
        :type: str

        Addon description string.
    
    .. attribute:: file_types
        :type: list[str]

        You can write like this: ``["txt","py", ....]``
    
    .. method:: __init__(api)

        Calls on file open. ``self`` will share.

        :param libmarusoftware.addon.AddonAPI api: AddonAPI. You will use this to control UI, settings, and etc... **Please keep this for later**

    .. method:: save(file=None)

        Calls on file saving.

        :param file: When "save as..." is selected, here comes new file path.
        :type file: str or None
    
    .. method:: new()

        Calls on new file created.
    
    .. method:: close()

        Calls on file closing.

On ``__init__``, api object will pass. api object has many api.
Please see :doc:`api`.

You can write just as python.
Happy coding!!