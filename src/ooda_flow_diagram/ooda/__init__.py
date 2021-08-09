import textwrap
import os

from pathlib import Path

class OodaNodeAttr(object):
    def __init__(self, subject: str, shape: str, style: str, fixedsize: str,
                 labelloc: str, width: str, height: str, fillcolor: str,
                 line_length: int, font_color: str, color: str,
                 gradientangle: str, margin: str = "0", pad: str = "0.0155",
                 penwidth: str = "1.0", peripheries: str = "1", method: str = 'singlecell',
                 subject2: str = "", subject3: str = "",):
        self._line_length = line_length
        self._method = method
        self._subjects = {
            'subject': subject,
            'subject2': subject2,
            'subject3': subject3,
        }
        # NodeにGraphvizの属性値として渡す属性で、かつinitで指定するもの
        # initで指定せずに、後から追加するものは、propertyにてセットする(URLなど)
        self._attrs = {
            "shape": shape,
            "style": style,
            "fixedsize": fixedsize,
            "labelloc": labelloc,
            "width": width,
            "height": height,
            "fillcolor": fillcolor,
            "gradientangle": gradientangle,
            "fontcolor": font_color,
            "margin": margin,
            "color": color,
            "pad": pad,
            "penwidth": penwidth,
            "peripheries": peripheries,


        }

    @property
    def attrs(self):
        return self._attrs

    @property
    def url(self):
        return self._attrs['URL']

    @url.setter
    def url(self, url: str):
        self._attrs['URL'] = url

    @property
    def line_length(self):
        return self._line_length

    @line_length.setter
    def line_length(self, line_length: int):
        if type(line_length) != int :
            raise TypeError('line_length:{} is not int.'.format(line_length))
        self._line_length = line_length

    def create_label(self, label, subject, line_mark, label2, subject2, line_mark2,
                     label3, subject3, line_mark3) -> str:
        """
        Switch create label string methods.
        """
        label_methods ={
            'singlecell': self._single_cell_label,
            'actcell1': self._act_cell_label,
            'acttable': self._act_table,
        }
        return label_methods[self._method](label, subject, line_mark, label2, subject2, line_mark2,
                                                    label3, subject3, line_mark3)

    def _single_cell_label(self, label, subject, line_mark, *args) -> str:
        label_cell = self._set_subject(subject, 'subject')
        label_cell = self._attached_url_str(label_cell)
        return self._write_label_cell(label_cell, label, line_mark)

    def _attached_url_str(self, label_cell) -> str:
        if self.url is not None:
            label_cell += "##Link Attached##\\n"
        return label_cell

    def _act_table(self, label, subject, line_mark, label2, subject2, line_mark2, label3: dict, *args) -> str:
        label_cell = '<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">'
        label_cell += '<tr><td>['+self._subjects['subject']+\
                      ']</td><td>' + self._load_icon(label3['progress']) + '</td></tr>'
        label_cell += '<tr><td colspan="2"  align="text">' + self._create_table_label(label, line_mark) + '</td></tr>'
        label_cell += '<tr><td colspan="2"><table border="0" cellpadding="0"><tr><td>[' + self._subjects['subject2'] + \
                      '] </td></tr><tr><td align="text">'
        label_cell += self._create_table_label(label2, line_mark2) + '</td></tr></table></td></tr>'
        label_cell += self._create_bywhen_who_tr(bywhen=label3['bywhen'], who=label3['who'])
        label_cell += self._create_completed_tr(completed_date=label3['completed_date'])
        label_cell += '</table>>'
        print(label_cell)
        return label_cell

    @staticmethod
    def _create_bywhen_who_tr(bywhen, who):
        label_cell = '<tr><td colspan="2" align="text">'
        if bywhen == "" and who == "":
            return ''
        elif bywhen == "" and who != "":
            label_cell += '[Who]: ' + who + '<br align="left" />'
        elif bywhen != "" and who == "":
            label_cell += '[ByWhen]: ' + bywhen + '<br align="left" />'
        else:  # bywhen != "" and who != "":
            label_cell += '[ByWhen]: ' + bywhen + \
                          '<br align="left" /> [Who]: ' + who + '<br align="left" />'
        label_cell += '</td></tr>'
        return label_cell

    @staticmethod
    def _create_completed_tr(completed_date: str):
        label_cell = '<tr><td colspan="2" align="text">'
        if completed_date == "":
            return ''
        else:
            label_cell += '[DoneDate]: ' + completed_date + '<br align="left" /></td></tr>'
            return label_cell

    @staticmethod
    def _load_icon(progress_rate: str):
        if progress_rate == 'start':
            image = 'start.png'
        elif progress_rate == '25':
            image = '25.png'
        elif progress_rate == '50':
            image = '50.png'
        elif progress_rate == '75':
            image = '75.png'
        elif progress_rate == 'done':
            image = 'done.png'
        else:
            return ''

        label = '<img src="'
        basedir = Path(os.path.abspath(os.path.dirname(__file__)))
        label += os.path.join(basedir.parent, 'ooda', 'img', image) + '"/>'
        return label

    def _create_table_label(self, label, line_mark) -> str:
        if type(label) == list:
            line_label = ""
            for index, item in enumerate(label):
                if line_mark == "point":
                    line_label += "・"
                elif line_mark == "seq":
                    line_label += str(index+1)+". "
                wrap_label = textwrap.wrap(item, self.line_length)
                line_label += '<br align="left" />　'.join(wrap_label)
                line_label += '<br align="left" />'
            return line_label

        elif type(label) == str:
            # 文字列をds_attr.line_length毎に改行して、self.labelにセット
            wrap_label = textwrap.wrap(label, self.line_length)
            label = '<br align="left"/>'.join(wrap_label)
            label += '<br align="left"/>'
            # subjectを部品固有のものを使うか、ユーザ指定のものを使うかを指定
            return label

    def _act_cell_label(self, label, subject, line_mark, label2, subject2, line_mark2,
                        label3: dict,
                        *args) -> str:
        label_cell = '{' + self._set_subject(subject, 'subject')
        label_cell = self._write_label_cell(label_cell, label, line_mark) + '|'
        label_cell += self._set_subject(subject2, 'subject2')
        label_cell = self._attached_url_str(label_cell)
        label_cell = self._write_label_cell(label_cell, label2, line_mark2)
        if label3['bywhen'] == "" and label3['who'] == "":
            label_cell += '}'
        elif label3['bywhen'] == "" and label3['who'] != "":
            label_cell += '| [Who]: ' + label3['who'] + '\\l}'
        elif label3['bywhen'] != "" and label3['who'] == "":
            label_cell += '| [ByWhen]: ' + label3['bywhen'] + '\\l}'
        else:  # label3['bywhen'] != "" and label3['who'] != "":
            label_cell += '| [ByWhen]: ' + label3['bywhen'] + '\\l[Who]: ' + label3['who'] + '\\l}'

        return label_cell

    def _write_label_cell(self, label_cell, label, line_mark) -> str:
        if type(label) == list:
            line_label = ""
            for index, item in enumerate(label):
                if line_mark == "point":
                    line_label += "・"
                elif line_mark == "seq":
                    line_label += str(index+1)+". "
                wrap_label = textwrap.wrap(item, self.line_length)
                line_label += '\\l　'.join(wrap_label)
                line_label += '\\l'
            label_cell += "{}".format(line_label)

        elif type(label) == str:
            # 文字列をds_attr.line_length毎に改行して、self.labelにセット
            wrap_label = textwrap.wrap(label, self.line_length)
            label = '\\n'.join(wrap_label)
            # subjectを部品固有のものを使うか、ユーザ指定のものを使うかを指定
            label_cell += "{}".format(label)
        return label_cell

    def _set_subject(self, subject, subject_key) -> str:
        if subject == "" and self._subjects[subject_key] != "":
            # default設定から、self._subjects[subject_key]に設定されている値に変更
            subject_created = "[{}]\\n".format(self._subjects[subject_key])
            return subject_created
        elif subject == "" and self._subjects[subject_key] == "":
            return ""
        else:
            subject_created = "[{}]\\n".format(subject)
            return subject_created

