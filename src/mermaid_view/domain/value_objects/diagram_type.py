"""Diagram type enumeration."""

from enum import Enum


class DiagramType(str, Enum):
    """Supported Mermaid diagram types."""

    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    STATE = "state"
    ER = "er"
    JOURNEY = "journey"
    GANTT = "gantt"
    PIE = "pie"
    QUADRANT = "quadrant"
    REQUIREMENT = "requirement"
    GITGRAPH = "gitgraph"
    C4 = "c4"
    MINDMAP = "mindmap"
    TIMELINE = "timeline"
    ZENUML = "zenuml"
    SANKEY = "sankey"
    XY = "xy"
    BLOCK = "block"
    PACKET = "packet"
    KANBAN = "kanban"
    ARCHITECTURE = "architecture"
    UNKNOWN = "unknown"

    @classmethod
    def detect_from_code(cls, code: str) -> "DiagramType":
        """Detect diagram type from Mermaid code.

        Args:
            code: The Mermaid diagram code.

        Returns:
            The detected DiagramType.
        """
        code_lower = code.strip().lower()

        # Check for each diagram type based on keywords
        type_keywords: dict[str, list[str]] = {
            cls.FLOWCHART: ["flowchart", "graph"],
            cls.SEQUENCE: ["sequencediagram", "sequence"],
            cls.CLASS: ["classdiagram", "class"],
            cls.STATE: ["statediagram", "state"],
            cls.ER: ["erdiagram", "er"],
            cls.JOURNEY: ["journey"],
            cls.GANTT: ["gantt"],
            cls.PIE: ["pie"],
            cls.QUADRANT: ["quadrantchart"],
            cls.REQUIREMENT: ["requirementdiagram"],
            cls.GITGRAPH: ["gitgraph"],
            cls.C4: ["c4context", "c4container", "c4component", "c4dynamic", "c4deployment"],
            cls.MINDMAP: ["mindmap"],
            cls.TIMELINE: ["timeline"],
            cls.ZENUML: ["zenuml"],
            cls.SANKEY: ["sankey"],
            cls.XY: ["xychart"],
            cls.BLOCK: ["block"],
            cls.PACKET: ["packet"],
            cls.KANBAN: ["kanban"],
            cls.ARCHITECTURE: ["architecture"],
        }

        for diagram_type, keywords in type_keywords.items():
            for keyword in keywords:
                if code_lower.startswith(keyword):
                    return diagram_type

        return cls.UNKNOWN
