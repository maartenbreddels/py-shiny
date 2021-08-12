"""
This type stub file was generated by pyright.
"""

"""Pylab (matplotlib) support utilities."""
backends = ...
backend2gui = ...
def getfigs(*fig_nums): # -> list[Unknown]:
    """Get a list of matplotlib figures by figure numbers.

    If no arguments are given, all available figures are returned.  If the
    argument list contains references to invalid figures, a warning is printed
    but the function continues pasting further figures.

    Parameters
    ----------
    figs : tuple
        A tuple of ints giving the figure numbers of the figures to return.
    """
    ...

def figsize(sizex, sizey): # -> None:
    """Set the default figure size to be [sizex, sizey].

    This is just an easy to remember, convenience wrapper that sets::

      matplotlib.rcParams['figure.figsize'] = [sizex, sizey]
    """
    ...

def print_figure(fig, fmt=..., bbox_inches=..., **kwargs): # -> str | bytes | None:
    """Print a figure to an image, and return the resulting file data
    
    Returned data will be bytes unless ``fmt='svg'``,
    in which case it will be unicode.
    
    Any keyword args are passed to fig.canvas.print_figure,
    such as ``quality`` or ``bbox_inches``.
    """
    ...

def retina_figure(fig, **kwargs): # -> tuple[str | bytes, dict[str, Any]] | None:
    """format a figure as a pixel-doubled (retina) PNG"""
    ...

def mpl_runner(safe_execfile): # -> (fname: Unknown, *where: Unknown, **kw: Unknown) -> None:
    """Factory to return a matplotlib-enabled runner for %run.

    Parameters
    ----------
    safe_execfile : function
      This must be a function with the same interface as the
      :meth:`safe_execfile` method of IPython.

    Returns
    -------
    A function suitable for use as the ``runner`` argument of the %run magic
    function.
    """
    ...

def select_figure_formats(shell, formats, **kwargs): # -> None:
    """Select figure formats for the inline backend.

    Parameters
    ==========
    shell : InteractiveShell
        The main IPython instance.
    formats : str or set
        One or a set of figure formats to enable: 'png', 'retina', 'jpeg', 'svg', 'pdf'.
    **kwargs : any
        Extra keyword arguments to be passed to fig.canvas.print_figure.
    """
    ...

def find_gui_and_backend(gui=..., gui_select=...): # -> tuple[Unknown | str | None, str | Unknown]:
    """Given a gui string return the gui and mpl backend.

    Parameters
    ----------
    gui : str
        Can be one of ('tk','gtk','wx','qt','qt4','inline','agg').
    gui_select : str
        Can be one of ('tk','gtk','wx','qt','qt4','inline').
        This is any gui already selected by the shell.

    Returns
    -------
    A tuple of (gui, backend) where backend is one of ('TkAgg','GTKAgg',
    'WXAgg','Qt4Agg','module://ipykernel.pylab.backend_inline','agg').
    """
    ...

def activate_matplotlib(backend): # -> None:
    """Activate the given backend and set interactive to True."""
    ...

def import_pylab(user_ns, import_all=...): # -> None:
    """Populate the namespace with pylab-related values.
    
    Imports matplotlib, pylab, numpy, and everything from pylab and numpy.
    
    Also imports a few names from IPython (figsize, display, getfigs)
    
    """
    ...

def configure_inline_support(shell, backend): # -> None:
    """Configure an IPython shell object for matplotlib use.

    Parameters
    ----------
    shell : InteractiveShell instance

    backend : matplotlib backend
    """
    ...

