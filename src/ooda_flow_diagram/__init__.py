import contextvars
import os
import uuid
from pathlib import Path
from typing import List, Union, Dict

from graphviz import Digraph

from ooda_flow_diagram.ooda import OodaNodeAttr

# Global contexts for a diagrams and a cluster.
#
# These global contexts are for letting the clusters and nodes know
# where context they are belong to. So the all clusters and nodes does
# not need to specify the current diagrams or cluster via parameters.
"""
これらのグローバルコンテキストは、クラスターとノードに、それらが属するコンテキストを知らせるためのものです。 したがって、すべてのクラスターとノードは
パラメータを介して現在のダイアグラムまたはクラスターを指定する必要はありません。
→おそらくこれを置いておくことで、継承する具体的なノードやクラスタをdiagramに属させるコードを書かなくてよくしている
"""
__diagram = contextvars.ContextVar("diagrams")
__cluster = contextvars.ContextVar("cluster")


def getdiagram():
    try:
        return __diagram.get()
    except LookupError:
        return None


def setdiagram(diagram):
    __diagram.set(diagram)


def getcluster():
    try:
        return __cluster.get()
    except LookupError:
        return None


def setcluster(cluster):
    __cluster.set(cluster)


class Diagram:
    __directions = ("TB", "BT", "LR", "RL")
    __curvestyles = ("ortho", "curved")
    __outformats = ("png", "jpg", "svg", "pdf")

    # fmt: off
    _default_graph_attrs = {
        "pad": "2.0",
        "splines": "ortho",
        "nodesep": "0.60",
        "ranksep": "0.75",
        "fontname": "Sans-Serif",
        "fontsize": "15",
        "fontcolor": "#2D3436",
        # cluster間のエッヂを有効にする
        "compound": "true",
    }
    _default_node_attrs = {
        "shape": "plaintext",
        "style": "rounded",
        "fixedsize": "true",
        "width": "1.4",
        "height": "1.4",
        "labelloc": "b",
        # imagepos attribute is not backward compatible
        # TODO: check graphviz version to see if "imagepos" is available >= 2.40
        # https://github.com/xflr6/graphviz/blob/master/graphviz/backend.py#L248
        # "imagepos": "tc",
        "imagescale": "true",
        "fontname": "Meiryo UI",

        # "fontname": "Sans-Serif",
        "fontsize": "13",
        "fontcolor": "#2D3436",
    }
    _default_edge_attrs = {
        "color": "#7B8894",
    }

    # fmt: on

    # TODO: Label position option
    # TODO: Save directory option (filename + directory?)
    def __init__(
        self,
        name: str = "",
        filename: str = "",
        direction: str = "LR",
        curvestyle: str = "ortho",
        outformat: str = "png",
        show: bool = True,
        label_loc: str = "t",
        graph_attr: dict = {},
        node_attr: dict = {},
        edge_attr: dict = {},
    ):
        """Diagram represents a global diagrams context.

        :param name: Diagram name. It will be used for output filename if the
            filename isn't given.
        :param filename: The output filename, without the extension (.png).
            If not given, it will be generated from the name.
        :param direction: Data flow direction. Default is 'left to right'.
        :param curvestyle: Curve bending style. One of "ortho" or "curved".
        :param outformat: Output file format. Default is 'png'.
        :param show: Open generated image after save if true, just only save otherwise.
        :param graph_attr: Provide graph_attr dot config attributes.
        :param node_attr: Provide node_attr dot config attributes.
        :param edge_attr: Provide edge_attr dot config attributes.
        """
        self.name = name
        if not name and not filename:
          filename = "diagrams_image"
        elif not filename:
            filename = "_".join(self.name.split()).lower()
        self.filename = filename
        self.dot = Digraph(self.name, filename=self.filename)

        # Set attributes.
        for k, v in self._default_graph_attrs.items():
            self.dot.graph_attr[k] = v
        self.dot.graph_attr["label"] = self.name
        for k, v in self._default_node_attrs.items():
            self.dot.node_attr[k] = v
        for k, v in self._default_edge_attrs.items():
            self.dot.edge_attr[k] = v

        if not self._validate_direction(direction):
            raise ValueError(f'"{direction}" is not a valid direction')
        self.dot.graph_attr["rankdir"] = direction

        if not self._validate_curvestyle(curvestyle):
            raise ValueError(f'"{curvestyle}" is not a valid curvestyle')
        self.dot.graph_attr["splines"] = curvestyle

        if not self._validate_outformat(outformat):
            raise ValueError(f'"{outformat}" is not a valid output format')
        self.outformat = outformat

        self.dot.graph_attr['labelloc'] = label_loc

        # Merge passed in attributes
        self.dot.graph_attr.update(graph_attr)
        self.dot.node_attr.update(node_attr)
        self.dot.edge_attr.update(edge_attr)

        self.show = show

    def __str__(self) -> str:
        return str(self.dot)

    def __enter__(self):
        # Diagramクラスをコンテキスト変数("diagram")にセット
        setdiagram(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.render()
        # Remove the graphviz file leaving only the image.
        os.remove(self.filename)
        setdiagram(None)

    def _repr_png_(self):
        return self.dot.pipe(format="png")

    def _validate_direction(self, direction: str) -> bool:
        direction = direction.upper()
        for v in self.__directions:
            if v == direction:
                return True
        return False

    def _validate_curvestyle(self, curvestyle: str) -> bool:
        curvestyle = curvestyle.lower()
        for v in self.__curvestyles:
            if v == curvestyle:
                return True
        return False

    def _validate_outformat(self, outformat: str) -> bool:
        outformat = outformat.lower()
        for v in self.__outformats:
            if v == outformat:
                return True
        return False

    def node(self, nodeid: str, label: str, **attrs) -> None:
        """Create a new node."""
        self.dot.node(nodeid, label=label, **attrs)

    def connect(self, node: "Node", node2: "Node", edge: "Edge") -> None:
        """Connect the two Nodes."""
        self.dot.edge(node.nodeid, node2.nodeid, **edge.attrs)

        # ここに入れると、上位のクラスタの設定が上書きされてします。
        # with self.dot.subgraph() as s:
        #     s.graph_attr['rank'] = 'same'
        #     s.edge(node.nodeid, node2.nodeid, **edge.attrs)

    def subgraph(self, dot: Digraph) -> None:
        """Create a subgraph for clustering"""
        self.dot.subgraph(dot)

    def render(self) -> None:
        self.dot.render(format=self.outformat, view=self.show, quiet=True)
        # ソース表示追加
        print(self.dot.source)


class Cluster:
    __directions = ("TB", "BT", "LR", "RL")
    __bgcolors = ("#E5F5FD", "#EBF3E7", "#ECE8F6", "#FDF7E3")

    # fmt: off
    _default_graph_attrs = {
        "shape": "box",
        "style": "rounded",
        "labeljust": "l",
        "pencolor": "#AEB6BE",
        "fontname": "Sans-Serif",
        "fontsize": "12",
        "pad": "0.0",
    }

    # fmt: on

    # FIXME:
    #  Cluster direction does not work now. Graphviz couldn't render
    #  correctly for a subgraph that has a different rank direction.
    def __init__(
        self, label: str = "cluster", direction: str = "LR", graph_attr: dict = {},
    ):
        """Cluster represents a cluster context.

        :param label: Cluster label.
        :param direction: Data flow direction. Default is 'left to right'.
        :param graph_attr: Provide graph_attr dot config attributes.
        """
        self.label = label
        self.name = "cluster_" + self.label

        self.dot = Digraph(self.name)

        # Set attributes.
        for k, v in self._default_graph_attrs.items():
            self.dot.graph_attr[k] = v
        self.dot.graph_attr["label"] = self.label

        if not self._validate_direction(direction):
            raise ValueError(f'"{direction}" is not a valid direction')
        self.dot.graph_attr["rankdir"] = direction
        # self.dot.graph_attr["rank"] = "same" きかない

        # Node must be belong to a diagrams.
        self._diagram = getdiagram()
        if self._diagram is None:
            raise EnvironmentError("Global diagrams context not set up")
        self._parent = getcluster()

        # Set cluster depth for distinguishing the background color
        self.depth = self._parent.depth + 1 if self._parent else 0
        coloridx = self.depth % len(self.__bgcolors)
        self.dot.graph_attr["bgcolor"] = self.__bgcolors[coloridx]

        # Merge passed in attributes
        self.dot.graph_attr.update(graph_attr)

    def __enter__(self):
        setcluster(self)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._parent:
            self._parent.subgraph(self.dot)
        else:
            self._diagram.subgraph(self.dot)
        setcluster(self._parent)


    def _validate_direction(self, direction: str):
        direction = direction.upper()
        for v in self.__directions:
            if v == direction:
                return True
        return False

    def node(self, nodeid: str, label: str, **attrs) -> None:
        """Create a new node in the cluster."""
        self.dot.node(nodeid, label=label, **attrs)

    def subgraph(self, dot: Digraph) -> None:
        self.dot.subgraph(dot)


class Node:
    """Node represents a node for a specific backend service."""

    _provider = None
    _type = None

    _icon_dir = None
    _icon = None
    _ds_attr: OodaNodeAttr = None

    _height = 1.9

    def __init__(self, label: Union[str, list] = "", label2: Union[str, list] = "",
                 label3: Union[str, list, dict] = "",
                 subject: str = "", subject2: str = "", subject3: str = "",
                 line_length: int = None, line_mark: str = "dot", line_mark2: str = "dot",
                 line_mark3: str = "dot",
                 url: str = None,
                 **attrs: Dict):
        """Node represents a system component.

        :param label: Node label.
        """
        # Generates an ID for identifying a node.
        self._id = self._rand_id()
        self.label = label

        # fmt: off
        # If a node has an icon, increase the height slightly to avoid
        # that label being spanned between icon image and white space.
        # Increase the height by the number of new lines included in the label.
        if self._icon:
            padding = 0.4 * (label.count('\n'))
            self._attrs = {
                "shape": "none",
                "height": str(self._height + padding),
                "image": self._load_icon(),
            }
        # Ds系の設定をここに追加している。
        elif self._ds_attr is not None:
            # line_lengthの更新
            if line_length is not None:
                self._ds_attr.line_length = line_length
            self._ds_attr.url = url
            self.label = self._ds_attr.create_label(
                label=label, subject=subject, line_mark=line_mark,
                label2=label2, subject2=subject2, line_mark2=line_mark2,
                label3=label3, subject3=subject3, line_mark3=line_mark3)
            # self._set_label(label, subject, line_mark)

            self._attrs = self._ds_attr.attrs

        else:
            self._attrs = {}

        # fmt: on
        self._attrs.update(attrs)

        # Node must be belong to a diagrams.
        self._diagram = getdiagram()
        if self._diagram is None:
            raise EnvironmentError("Global diagrams context not set up")
        self._cluster = getcluster()

        # If a node is in the cluster context, add it to cluster.
        if self._cluster:
            self._cluster.node(self._id, self.label, **self._attrs)
        else:
            self._diagram.node(self._id, self.label, **self._attrs)

    def __repr__(self):
        _name = self.__class__.__name__
        return f"<{self._provider}.{self._type}.{_name}>"

    def __add__(self, other: "Node"):
        if isinstance(other, Node):
            with self._diagram.dot.subgraph() as s:
                s.graph_attr['rank'] = 'same'
                other.connect(self, Edge(self))

    def __sub__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implement Self - Node, Self - [Nodes] and Self - Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self))
        else:
            other.node = self
            return other

    def __rsub__(self, other: Union[List["Node"], List["Edge"]]):
        """ Called for [Nodes] and [Edges] - Self because list don't have __sub__ operators. """
        for o in other:
            if isinstance(o, Edge):
                o.connect(self)
            else:
                o.connect(self, Edge(self))
        return self

    def __rshift__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implements Self >> Node, Self >> [Nodes] and Self Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self, forward=True))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self, forward=True))
        else:
            other.forward = True
            other.node = self
            return other

    def __lshift__(self, other: Union["Node", List["Node"], "Edge"]):
        """Implements Self << Node, Self << [Nodes] and Self << Edge."""
        if isinstance(other, list):
            for node in other:
                self.connect(node, Edge(self, reverse=True))
            return other
        elif isinstance(other, Node):
            return self.connect(other, Edge(self, reverse=True))
        else:
            other.reverse = True
            return other.connect(self)

    def __rrshift__(self, other: Union[List["Node"], List["Edge"]]):
        """Called for [Nodes] and [Edges] >> Self because list don't have __rshift__ operators."""
        for o in other:
            if isinstance(o, Edge):
                o.forward = True
                o.connect(self)
            else:
                o.connect(self, Edge(self, forward=True))
        return self

    def __rlshift__(self, other: Union[List["Node"], List["Edge"]]):
        """Called for [Nodes] << Self because list of Nodes don't have __lshift__ operators."""
        for o in other:
            if isinstance(o, Edge):
                o.reverse = True
                o.connect(self)
            else:
                o.connect(self, Edge(self, reverse=True))
        return self

    @property
    def nodeid(self):
        return self._id

    # TODO: option for adding flow description to the connection edge
    def connect(self, node: "Node", edge: "Edge"):
        """Connect to other node.

        :param node: Other node instance.
        :param edge: Type of the edge.
        :return: Connected node.
        """
        if not isinstance(node, Node):
            ValueError(f"{node} is not a valid Node")
        if not isinstance(edge, Edge):
            ValueError(f"{edge} is not a valid Edge")
        # An edge must be added on the global diagrams, not a cluster.
        self._diagram.connect(self, node, edge)
        return node

    @staticmethod
    def _rand_id():
        return uuid.uuid4().hex

    def _load_icon(self):
        basedir = Path(os.path.abspath(os.path.dirname(__file__)))
        return os.path.join(basedir.parent, self._icon_dir, self._icon)







class Edge:
    """Edge represents an edge between two nodes."""

    _default_edge_attrs = {
        "fontcolor": "#2D3436",
        "fontname": "Sans-Serif",
        "fontsize": "13",
    }

    def __init__(
        self,
        node: "Node" = None,
        forward: bool = False,
        reverse: bool = False,
        label: str = "",
        color: str = "",
        style: str = "",
        ltail: str = "",
        lhead: str = "",
        **attrs: Dict,
    ):
        """Edge represents an edge between two nodes.

        :param node: Parent node.
        :param forward: Points forward.
        :param reverse: Points backward.
        :param label: Edge label.
        :param color: Edge color.
        :param style: Edge style.
        :param attrs: Other edge attributes
        """
        if node is not None:
            assert isinstance(node, Node)

        self.node = node
        self.forward = forward
        self.reverse = reverse

        self._attrs = {}

        # Set attributes.
        for k, v in self._default_edge_attrs.items():
            self._attrs[k] = v

        if label:
            # Graphviz complaining about using label for edges, so replace it with xlabel.
            # Update: xlabel option causes the misaligned label position: https://github.com/mingrammer/diagrams/issues/83
            self._attrs["label"] = label
        if color:
            self._attrs["color"] = color
        if style:
            self._attrs["style"] = style
        if ltail:
            self._attrs["ltail"] = "cluster_"+ltail
        if lhead:
            self._attrs["lhead"] = "cluster_"+lhead
        self._attrs.update(attrs)

    def __sub__(self, other: Union["Node", "Edge", List["Node"]]):
        """Implement Self - Node or Edge and Self - [Nodes]"""
        return self.connect(other)

    def __rsub__(self, other: Union[List["Node"], List["Edge"]]) -> List["Edge"]:
        """Called for [Nodes] or [Edges] - Self because list don't have __sub__ operators."""
        return self.append(other)

    def __rshift__(self, other: Union["Node", "Edge", List["Node"]]):
        """Implements Self >> Node or Edge and Self >> [Nodes]."""
        self.forward = True
        return self.connect(other)

    def __lshift__(self, other: Union["Node", "Edge", List["Node"]]):
        """Implements Self << Node or Edge and Self << [Nodes]."""
        self.reverse = True
        return self.connect(other)

    def __rrshift__(self, other: Union[List["Node"], List["Edge"]]) -> List["Edge"]:
        """Called for [Nodes] or [Edges] >> Self because list of Edges don't have __rshift__ operators."""
        return self.append(other, forward=True)

    def __rlshift__(self, other: Union[List["Node"], List["Edge"]]) -> List["Edge"]:
        """Called for [Nodes] or [Edges] << Self because list of Edges don't have __lshift__ operators."""
        return self.append(other, reverse=True)

    def append(self, other: Union[List["Node"], List["Edge"]], forward=None, reverse=None) -> List["Edge"]:
        result = []
        for o in other:
            if isinstance(o, Edge):
                o.forward = forward if forward else o.forward
                o.reverse = forward if forward else o.reverse
                self._attrs = o.attrs.copy()
                result.append(o)
            else:
                result.append(Edge(o, forward=forward, reverse=reverse, **self._attrs))
        return result

    def connect(self, other: Union["Node", "Edge", List["Node"]]):
        if isinstance(other, list):
            for node in other:
                self.node.connect(node, self)
            return other
        elif isinstance(other, Edge):
            self._attrs = other._attrs.copy()
            return self
        else:
            if self.node is not None:
                return self.node.connect(other, self)
            else:
                self.node = other
                return self

    @property
    def attrs(self) -> Dict:
        if self.forward and self.reverse:
            direction = "both"
        elif self.forward:
            direction = "forward"
        elif self.reverse:
            direction = "back"
        else:
            direction = "none"
        return {**self._attrs, "dir": direction}


Group = Cluster