import os
import re

from .file import Kind as File


class Kind(File):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = "keymap"
        self.default_action = "execute"
        self.redraw_actions += ["delete", "unmap"]
        self.persist_actions += ["delete", "unmap"]

    def action_execute(self, context):
        target = context["targets"][0]

        # execute only normal mode keymap
        if "n" not in target["action__mode"]:
            return

        # ex. <CR> -> \<CR>
        lhs = re.sub("<(?=(.+)>)", "\\<", target["action__lhs"])

        # ^\<Space> -> ^1\<Space>
        # help :normal
        lhs = re.sub("(?=^\\\\<Space>)", "1", lhs)

        command = "normal {}".format(lhs)
        self.vim.command('execute "{}"'.format(command))

    def action_delete(self, context):
        for target in context["targets"]:
            # ex. mode = nox -> nunmap, ounmap, xunmap
            for mode in target["action__mode"]:
                self.vim.command("{}unmap {}".format(mode, target["action__lhs"]))

    def action_open(self, context):
        self._open(context, "edit")

    def action_drop(self, context):
        self._open(context, "drop")

    def action_tabopen(self, context):
        self._open(context, "tabedit")

    def _open(self, context, cmd):
        new_targets = []
        # FIXME <Space>, <lt>
        escaped = "[]=|\\(){}<>%/&$^~@?"
        for target in context["targets"]:
            lhs = target["action__lhs"]
            path, line = self._get_file_path(lhs)
            if path is None:
                continue

            pattern = "\\v\\c.*map.*{}\\s+{}".format(
                self.vim.call("escape", lhs, escaped),
                self.vim.call("escape", target["action__rhs"], escaped),
            )
            target["action__path"] = path
            if line is not None:
                target["action__line"] = line
            else:
                target["action__pattern"] = pattern
            new_targets.append(target)

        context["targets"] = new_targets
        super()._open(context, cmd)

    def action_unmap(self, context):
        # alias unmap=delete
        self.action_delete(context)

    def _get_file_path(self, lhs):
        cmd = "verbose map {}".format(lhs)
        map_output = list(
            filter(
                lambda x: x != "",
                self.vim.call("denite_keymap#util#redir", cmd).split("\n"),
            )
        )
        if len(map_output) < 2:
            return None

        paths = map_output[1].split()
        if len(paths) == 0:
            return None

        path = os.path.expanduser(paths[-3])
        if not os.path.isfile(path):
            return None, None

        line = int(paths[-1]) if paths[-1].isdigit() else None

        return path, line
