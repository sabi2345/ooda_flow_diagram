from typing import Union

from ooda_flow_diagram import Node
from ooda_flow_diagram.ooda import OodaNodeAttr


class MajorTarget(Node):
    _ds_attr = OodaNodeAttr(
        subject="Major Target", shape="tripleoctagon", style='filled', fixedsize='false',
        fillcolor="#354093:#354093", gradientangle="225",
        labelloc='t', height="0.75", width="0.5", line_length=40,
        font_color="white", color="#354093", peripheries="3")

    def __init__(self, label: Union[str, list], line_length: int = None, line_mark: str = "dot",
                 subject: str = 'Major Target'):
        super().__init__(label=label, line_length=line_length, line_mark= line_mark, subject=subject)


class Target(Node):
    _ds_attr = OodaNodeAttr(
        subject="Target", shape="doubleoctagon", style='filled', fixedsize='false',
        fillcolor="#354093:#354093", gradientangle="225",
        labelloc='t', height="0.75", width="0.5", line_length=40,
        font_color="white", color="#354093", peripheries="2")

    def __init__(self, label: Union[str, list], line_length: int = None, line_mark: str = "dot",
                 subject: str = 'Target'):
        super().__init__(label=label, line_length=line_length, line_mark= line_mark, subject=subject)


class MajorPrerequisite(Node):
    _ds_attr = OodaNodeAttr(
        subject="MajorPrerequisite", shape="tripleoctagon", style='filled', fixedsize='false',
        fillcolor="#1E88A8:#006284", gradientangle="225",
        labelloc='t', height="0.75", width="0.5", line_length=40,
        font_color="white", color="#1E88A8", peripheries="3")

    def __init__(self, label: Union[str, list], line_length: int = None, line_mark: str = "dot",
                 subject: str = 'MajorPrerequisite'):
        super().__init__(label=label, line_length=line_length, line_mark= line_mark, subject=subject)


class Prerequisite(Node):
    _ds_attr = OodaNodeAttr(
        subject="Prequisite", shape="doubleoctagon", style='filled', fixedsize='false',
        fillcolor="#1E88A8:#006284", gradientangle="225",
        labelloc='t', height="0.75", width="0.5", line_length=40,
        font_color="white", color="#1E88A8", peripheries="2")

    def __init__(self, label: Union[str, list], line_length: int = None, line_mark: str = "dot",
                 subject: str = 'Prerequisite'):
        super().__init__(label=label, line_length=line_length, line_mark= line_mark, subject=subject)


class ActCells(Node):
    _ds_attr = OodaNodeAttr(
        subject="ToDo", subject2="Output", subject3="ByWhen", shape="record", style='solid,filled', margin="0.1",
        fixedsize='false', method="actcell1",
        fillcolor= "#c2e6f9:#c2e6f9", gradientangle="225",
        labelloc='c', height="0.5", width="0.6", line_length=40,
        font_color="#000b00", color="#383c3c", penwidth="1.0", peripheries="2")

    def __init__(self, todo="", output="", bywhen="", who="", first_subject: str = "", second_subject: str = "",
                 third_subject: str = "",
                 line_length: int = None, line_mark: str = "dot", line_mark2: str = "dot", line_mark3: str = "dot",
                 output_url: str = None):
        super().__init__(label=todo, label2=output, label3={'bywhen': bywhen, 'who': who}, subject=first_subject,
                         subject2=second_subject, subject3=third_subject,
                         line_length=line_length, line_mark=line_mark, line_mark2=line_mark2,
                         line_mark3=line_mark3, url=output_url)


class ActTable(Node):
    _ds_attr = OodaNodeAttr(
        subject="ToDo", subject2="Output", subject3="ByWhen", shape="record", style='filled', margin="0",
        fixedsize='false', method="acttable",
        fillcolor="#c2e6f9:#c2e6f9", gradientangle="225",
        labelloc='c', height="0.5", width="2.0", line_length=40,
        font_color="#000b00", color="#383c3c", penwidth="1.0", peripheries="2")

    def __init__(self, todo="", output="", bywhen="", who="", first_subject: str = "", second_subject: str = "",
                 third_subject: str = "",
                 line_length: int = None, todo_mark: str = "point", output_mark: str = "point",
                 output_url: str = None, completed_date: str = "", progress: str = ""):
        super().__init__(label=todo, label2=output,
                         label3={'bywhen': bywhen, 'who': who, 'completed_date': completed_date, 'progress': progress},
                         subject=first_subject, subject2=second_subject, subject3=third_subject,
                         line_length=line_length, line_mark=todo_mark, line_mark2=output_mark,
                         url=output_url)


class Result(Node):
    _ds_attr = OodaNodeAttr(
        subject="", shape="box", style='rounded,filled', margin="0.1",
        fixedsize='false',
        fillcolor="#3B74BF:#3B74BF", gradientangle="225",
        labelloc='c', height="0.5", width="0.6", line_length=40,
        font_color="white", color="#005CAF", peripheries="2",
        )

    def __init__(self, label: Union[str, list] = "", subject: str = "",
                 line_length: int = None, line_mark: str = "dot", output_url: str = None):
        super().__init__(label=label, subject=subject, line_length=line_length, line_mark= line_mark, url=output_url)