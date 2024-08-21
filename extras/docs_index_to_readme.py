"""Converts the pt_docs index.rst file into README.rst."""
import re


def fix_tags(line):
    return re.sub(r':(mod|func|data|const|class|meth|attr|type|exc|obj):`~?([^`]+)`', r'``\2``', line)


with open('pyterrier_anserini/pt_docs/index.rst') as fin, \
     open('README.rst', 'wt') as fout:
    fout.write('''.. NOTE: this file was generated from pyterrier_anserini/pt_docs/index.rst. Changes made to README.rst may be reverted.
.. Make any changes to pyterrier_anserini/pt_docs/index.rst instead.

''')
    mode = 'normal'
    for line in fin:
        if mode == 'normal':
            if line == '.. BEGIN_README_SKIP\n':
                mode = 'skip'
            elif line == '.. BEGIN_README_INCLUDE\n':
                mode = 'include'
            else:
                fout.write(fix_tags(line))
        elif mode == 'skip':
            if line == '.. END_README_SKIP\n':
                mode = 'normal'
        elif mode == 'include':
            if line == '.. BEGIN_README_INCLUDE\n':
                mode = 'normal'
            else:
                if line.startswith('.. '):
                    line = line[3:]
                fout.write(fix_tags(line))
