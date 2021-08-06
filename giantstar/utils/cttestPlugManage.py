# _*_encoding=utf8_*_
# @Time : 2021/6/5 15:03 

# @Author : xuyong

# @Email: yong1.xu@casstime.com
import inspect

from pluggy import PluginManager
from giantstar.utils import hookspec


class CttestPluginManager(PluginManager):
    def __init__(self):
        super().__init__("cttest")
        self.add_hookspecs(hookspec)
        self.register(self)

    def parse_hookimpl_opts(self, plugin, name):
        if not name.startswith("cttest_"):
            return

        method = getattr(plugin, name)
        opts = super().parse_hookimpl_opts(plugin, name)

        if not inspect.isroutine(method):
            return

        if opts is None and name.startswith("cttest_"):
            opts = {}

        if opts is not None:
            known_marks = {m.name for m in getattr(method, "cttestmark", [])}

            for name in ("tryfirst", "trylast", "optionalhook", "hookwrapper"):
                opts.setdefault(name, hasattr(method, name) or name in known_marks)
        return opts

    def parse_hookspec_opts(self, module_or_class, name):
        opts = super().parse_hookspec_opts(module_or_class, name)
        if opts is None:
            method = getattr(module_or_class, name)
            if name.startswith("cttest_"):
                known_marks = {m.name for m in getattr(method, "cttestmark", [])}
                opts = {
                    "firstresult": hasattr(method, "firstresult")
                    or "firstresult" in known_marks,
                    "historic": hasattr(method, "historic")
                    or "historic" in known_marks,
                }
        return opts
