import sys
import os
import tempfile
import base64
import mimetypes
import inspect
from typing import TYPE_CHECKING, Callable, Literal, Optional, Awaitable, Union
import typing

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

from htmltools import TagChildArg

if TYPE_CHECKING:
    from .shinysession import ShinySession

from . import utils


UserRenderFunction = Callable[[], object]
UserRenderFunctionAsync = Callable[[], Awaitable[object]]


class ImgData(TypedDict):
    src: str
    width: Union[str, float]
    height: Union[str, float]
    alt: Optional[str]


ImgRenderFunc = Callable[[], ImgData]
ImgRenderFuncAsync = Callable[[], Awaitable[ImgData]]


class RenderFunction:
    def __init__(self, fn: UserRenderFunction) -> None:
        raise NotImplementedError

    def __call__(self) -> object:
        raise NotImplementedError

    def set_metadata(self, session: "ShinySession", name: str) -> None:
        """When RenderFunctions are assigned to Output object slots, this method
        is used to pass along session and name information.
        """
        self._session: ShinySession = session
        self._name: str = name


class RenderFunctionAsync(RenderFunction):
    async def __call__(self) -> object:
        raise NotImplementedError


class Plot(RenderFunction):
    _ppi: float = 96

    def __init__(self, fn: UserRenderFunction, alt: Optional[str] = None) -> None:
        self._fn: UserRenderFunctionAsync = utils.wrap_async(fn)
        self._alt: Optional[str] = alt

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        # Reactively read some information about the plot.
        pixelratio: float = typing.cast(
            float, self._session.input[".clientdata_pixelratio"]
        )
        width: float = typing.cast(
            float, self._session.input[f".clientdata_output_{self._name}_width"]
        )
        height: float = typing.cast(
            float, self._session.input[f".clientdata_output_{self._name}_height"]
        )

        fig = await self._fn()

        if fig is None:
            return None

        # Try each type of renderer in turn. The reason we do it this way is to avoid
        # importing modules that aren't already loaded. That could slow things down, or
        # worse, cause an error if the module isn't installed.
        #
        # Each try_render function should return either an ImgResult, None (which
        # indicates that the rendering failed), or the string "TYPE_MISMATCH" (which
        # indicate that `fig` object was not the type of object that the renderer knows
        # how to handle). In the case of a "TYPE_MISMATCH", it will move on to the next
        # renderer.
        result: Union[ImgData, None, Literal["TYPE_MISMATCH"]] = None
        if "matplotlib" in sys.modules:
            result = try_render_plot_matplotlib(
                fig, width, height, pixelratio, self._ppi
            )
            if result != "TYPE_MISMATCH":
                return result

        raise Exception("Unsupported figure type: " + str(type(fig)))


class PlotAsync(Plot, RenderFunctionAsync):
    def __init__(self, fn: UserRenderFunctionAsync, alt: Optional[str] = None) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("PlotAsync requires an async function")

        # Init the Plot base class with a placeholder synchronous function so it
        # won't throw an error, then replace it with the async function.
        super().__init__(lambda: None, alt)
        self._fn: UserRenderFunctionAsync = fn

    async def __call__(self) -> object:
        return await self.run()


def plot(alt: Optional[str] = None):
    def wrapper(fn: Union[UserRenderFunction, UserRenderFunctionAsync]) -> Plot:
        if inspect.iscoroutinefunction(fn):
            fn = typing.cast(UserRenderFunctionAsync, fn)
            return PlotAsync(fn, alt=alt)
        else:
            return Plot(fn, alt=alt)

    return wrapper


# Try to render a matplotlib object. If `fig` is not a matplotlib object, return
# "TYPE_MISMATCH". If there's an error in rendering, return None. If successful in
# rendering, return an ImgData object.
def try_render_plot_matplotlib(
    fig: object,
    width: float,
    height: float,
    pixelratio: float,
    ppi: float,
    alt: Optional[str] = None,
) -> Union[ImgData, None, Literal["TYPE_MISMATCH"]]:
    import matplotlib.figure
    import matplotlib.pyplot

    if isinstance(fig, matplotlib.figure.Figure):
        tmpfile = tempfile.mkstemp(suffix=".png")[1]

        try:
            fig.set_dpi(ppi * pixelratio)
            fig.set_size_inches(width / ppi, height / ppi)

            fig.savefig(tmpfile)

            with open(tmpfile, "rb") as image_file:
                data = base64.b64encode(image_file.read())
                data_str = data.decode("utf-8")

            res: ImgData = {
                "src": "data:image/png;base64," + data_str,
                "width": width,
                "height": height,
                "alt": alt,
            }

            return res

        except Exception as e:
            # TODO: just let errors propagate?
            print("Error rendering matplotlib object: " + str(e))

        finally:
            matplotlib.pyplot.close(fig)
            os.remove(tmpfile)

        return None

    else:
        return "TYPE_MISMATCH"


class Image(RenderFunction):
    def __init__(self, fn: ImgRenderFunc, delete_file: bool = False) -> None:
        self._fn: ImgRenderFuncAsync = utils.wrap_async(fn)
        self._delete_file: bool = delete_file

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        res: ImgData = await self._fn()
        src: str = res.get("src")
        try:
            with open(src, "rb") as f:
                data = base64.b64encode(f.read())
                data_str = data.decode("utf-8")
            content_type = mimetypes.guess_type(src)[1]
            res["src"] = f"data:{content_type};base64,{data_str}"
            return res
        finally:
            if self._delete_file:
                os.remove(src)


class ImageAsync(Image, RenderFunctionAsync):
    def __init__(self, fn: ImgRenderFuncAsync, delete_file: bool = False) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("PlotAsync requires an async function")
        # Init the Plot base class with a placeholder synchronous function so it
        # won't throw an error, then replace it with the async function.
        super().__init__(lambda: None, delete_file)
        self._fn: ImgRenderFuncAsync = fn

    async def __call__(self) -> object:
        return await self.run()


def image(delete_file: bool = False):
    def wrapper(fn: Union[ImgRenderFunc, ImgRenderFuncAsync]) -> Image:
        if inspect.iscoroutinefunction(fn):
            fn = typing.cast(ImgRenderFuncAsync, fn)
            return ImageAsync(fn, delete_file=delete_file)
        else:
            fn = typing.cast(ImgRenderFunc, fn)
            return Image(fn, delete_file=delete_file)

    return wrapper


UiRenderFunc = Callable[[], TagChildArg]
UiRenderFuncAsync = Callable[[], Awaitable[TagChildArg]]


class UI(RenderFunction):
    def __init__(self, fn: UiRenderFunc) -> None:
        self._fn: UiRenderFuncAsync = utils.wrap_async(fn)

    def __call__(self) -> object:
        return utils.run_coro_sync(self.run())

    async def run(self) -> object:
        ui: TagChildArg = await self._fn()
        if ui is None:
            return None
        return utils.process_deps(ui, self._session)


class UIAsync(UI, RenderFunctionAsync):
    def __init__(self, fn: UiRenderFuncAsync) -> None:
        if not inspect.iscoroutinefunction(fn):
            raise TypeError("PlotAsync requires an async function")

        super().__init__(lambda: None)
        self._fn: UiRenderFuncAsync = fn

    async def __call__(self) -> object:
        return await self.run()


def ui():
    def wrapper(fn: Union[UiRenderFunc, UiRenderFuncAsync]) -> UI:
        if inspect.iscoroutinefunction(fn):
            fn = typing.cast(UiRenderFuncAsync, fn)
            return UIAsync(fn)
        else:
            fn = typing.cast(UiRenderFunc, fn)
            return UI(fn)

    return wrapper
