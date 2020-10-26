import os
import subprocess
import compas

HERE = os.path.dirname(os.path.realpath(__file__))


def Browser():
    from zipfile import ZipFile

    if compas.MONO:
        BIN = os.path.join(HERE, 'electron', 'frontpage.app', 'Contents', 'MacOS', 'frontpage')

        if not os.path.exists(BIN):
            print("Init page skipped. To enable it, go to src/compas_rv2/web, delete electron folder, then run: npm install && npm run build")
        else:
            subprocess.Popen('%s' % BIN)

    else:
        BIN = os.path.join(HERE, 'electron', 'frontpage.exe')

        if not os.path.exists(BIN):
            print("unziping electron front page for dev install, this will take a while...")
            zf = ZipFile(os.path.join(HERE, 'electron.zip'), 'r')
            zf.extractall(os.path.join(HERE, 'electron'))
            zf.close()

        subprocess.Popen('"%s"' % BIN)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    Browser()
