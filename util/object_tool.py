from typing import Iterable


class ObjectTool:

    @staticmethod
    def any_none(*objs: Iterable) -> bool:

        for _ in objs:
            if _ is None:
                return True

        return False