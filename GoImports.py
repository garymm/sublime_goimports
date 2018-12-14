# Sublime Text 3 Plugin that integrates goimports with your favorite editor
#
# Author: Lukas Zilka (lukas@zilka.me)
#
import sublime
import sublime_plugin
import subprocess
import io
import os

MY_PATH = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(MY_PATH, "bin/goimports")

def install():
    script = [
        "GOPATH='%s' go get github.com/bradfitz/goimports" % MY_PATH
    ]
    for ln in script:
        p = subprocess.Popen(ln, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.wait():
            print("Error when installing goimports:")
            print(p.stdout.read())
            print(p.stderr.read())

s = sublime.load_settings("GoImports.sublime-settings")
settings_path = s.get("goimports_bin_path")
if settings_path:
    bin_path = settings_path
elif not os.path.exists(bin_path):
    install()


class GoImportsCommand(sublime_plugin.TextCommand):
    def run(self, edit, saving=False):
        # Get the content of the current window from the text editor.
        selection = sublime.Region(0, self.view.size())
        content = self.view.substr(selection)

        # Shove that content down goimports process's throat.
        process = subprocess.Popen([bin_path],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.stdin.write(bytes(content, 'utf8'))
        process.stdin.close()
        process.wait()

        # Check and see if we got an error
        error = process.stderr.read().decode('utf8')
        if error:
            print("error: " + error)
        else:
            self.view.replace(edit, selection, process.stdout.read().decode('utf8'))
