import hashlib
import unittest

from olpkit.nativefigures import extract_tikz


class NativeFigureTests(unittest.TestCase):
    def test_only_live_diagrams_are_extracted_with_exact_offsets(self):
        picture = r'\begin{tikzpicture}\node{$q_0$};\end{tikzpicture}'
        source = (r'\newcommand{\unused}{'+picture+'}\n' +
                  '% '+picture+'\n'+r'\begin{verbatim}'+picture+r'\end{verbatim}' +
                  'before{'+picture+'}after'+picture)
        rows = extract_tikz(source)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertEqual(row['source_tex'], picture)
            self.assertEqual(source[row['char_start']:row['char_end']], picture)
            self.assertEqual(row['source_sha256'], hashlib.sha256(picture.encode()).hexdigest())

    def test_placement_and_labels_are_not_normalized(self):
        source = '\\begin{tikzpicture}[->]\n  \\node[initial,state] (A) {$q_{10}$};\n% comment\n\\end{tikzpicture}'
        self.assertEqual(extract_tikz(source)[0]['source_tex'], source)

    def test_unclosed_picture_fails(self):
        with self.assertRaisesRegex(ValueError, 'unclosed environment'):
            extract_tikz(r'\begin{tikzpicture}\node{x};')


if __name__ == '__main__': unittest.main()
