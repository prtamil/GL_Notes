import os,sys

class DirWalker:
    def walk(self, dir, meth):
        dir = os.path.abspath(dir)
        for file in [file for file in os.listdir(dir) if not file in [".",".."]]:
            nfile = os.path.join(dir,file)
            meth(nfile)
            if os.path.isdir(nfile):
                self.walk(nfile,meth)


d = DirWalker()
d.walk(".",print)
