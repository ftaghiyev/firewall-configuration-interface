import { useCallback, useMemo, useState } from "react";
import {
  ReactFlow,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  type Node,
  type Edge,
  type OnConnect,
  type OnNodesChange,
  type OnEdgesChange,
  type OnNodeDrag,
  Controls,
  Background,
  Position,
  Handle,
  NodeResizer,
  Panel,
  useReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { JsonView, darkStyles, collapseAllNested } from "react-json-view-lite";
import "react-json-view-lite/dist/index.css";
import { Label } from "../ui/label";
import dagre from "dagre";
import { Button } from "../ui/button";
import { LuLayoutTemplate } from "react-icons/lu";

interface PipelineGraphProps {
  policyId: string;
  resolverOutput: any;
  irOutput: any;
  lintingWarnings: Record<string, string[]>;
  safetyWarnings: string[];
  batfishWarnings: { severity: string; message: string }[];
  configs: Record<string, string>;
}

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 280;
const nodeHeight = 300;

const getLayoutedElements = (nodes: Node[], edges: Edge[]) => {
  dagreGraph.setGraph({ rankdir: "TB" });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: (node.style?.width as number) || nodeWidth,
      height: (node.measured?.height as number) || (node.style?.height as number) || nodeHeight,
    });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  return nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
      position: {
        x: nodeWithPosition.x - ((node.style?.width as number) || nodeWidth) / 2,
        y: nodeWithPosition.y - ((node.measured?.height as number) || (node.style?.height as number) || nodeHeight) / 2,
      },
    };
  });
};

export default function PipelineGraph({
  policyId,
  resolverOutput,
  irOutput,
  lintingWarnings,
  safetyWarnings,
  batfishWarnings,
  configs,
}: PipelineGraphProps) {
  // const { fitView } = useReactFlow(); // Can't use inside the component rendering ReactFlowProvider unless wrapped.
  // We can use the instance from onInit or store it. But here we can just update nodes.

  const initialNodes: Node[] = useMemo(
    () => [
      {
        id: "resolver",
        position: { x: 40, y: 20 },
        data: {
          label: "Resolver Output",
          json: resolverOutput,
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: "#1f2937",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
      {
        id: "ir",
        position: { x: 40, y: 380 },
        data: {
          label: "IR Builder Output",
          json: irOutput,
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: "#1f2937",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
      {
        id: "linting",
        position: { x: 360, y: 660 },
        data: {
          label: "Linter Analysis",
          json:
            Object.keys(lintingWarnings).length > 0
              ? lintingWarnings
              : ["No linter warnings"],
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background:
            Object.keys(lintingWarnings).length > 0 ? "#b45309" : "#065f46",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
      {
        id: "safety",
        position: { x: 40, y: 800 },
        data: {
          label: "Safety Gate",
          json:
            safetyWarnings.length > 0 ? safetyWarnings : ["No safety warnings"],
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: safetyWarnings.length > 0 ? "#b45309" : "#065f46",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },

      {
        id: "configs",
        position: { x: 40, y: 1000 },
        data: {
          label: "Compiled Configurations",
          json: configs,
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: "#1f2937",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },

      {
        id: "batfish",
        position: { x: 360, y: 1200 },
        data: {
          label: "Batfish Analysis",
          json:
            batfishWarnings && batfishWarnings.length > 0
              ? batfishWarnings
              : ["Batfish validation successful"],
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background:
            batfishWarnings && batfishWarnings.length > 0
              ? batfishWarnings.some((w) => w.severity === "error")
                ? "#7f1d1d" // Red for errors
                : "#b45309" // Orange for warnings
              : "#065f46", // Green for success
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
    ],
    [
      resolverOutput,
      irOutput,
      lintingWarnings,
      safetyWarnings,
      batfishWarnings,
      configs,
    ]
  );

  const edgesRaw = [
    ["resolver", "ir"],
    ["ir", "linting"],
    ["ir", "safety"],
    ["safety", "configs"],
    ["configs", "batfish"],
  ];
  const initialEdges = edgesRaw.map(([source, target]) => ({
    id: `${source}-to-${target}`,
    source: source,
    target: target,
    type: "smoothstep",
    animated: true,
    style: { stroke: "#60a5fa", strokeWidth: 2 },
  }));

  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );
  const onConnect: OnConnect = useCallback(
    (connection) => setEdges((eds) => addEdge(connection, eds)),
    [setEdges]
  );

  const onNodeDrag: OnNodeDrag = (_, node) => {
    console.log("drag event", node.data);
  };

  const onLayout = useCallback(() => {
    const layoutedNodes = getLayoutedElements(nodes, edges);
    setNodes([...layoutedNodes]);
  }, [nodes, edges]);

  const nodeTypes = {
    jsonNode: JsonNode,
  };

  const initialViewport = {
    x: 0,
    y: 0,
    zoom: 0.8,
  };

  return (
    <div className="w-full h-full">
      <Label>Policy ID: {policyId}</Label>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeDrag={onNodeDrag}
        nodeTypes={nodeTypes}
        defaultViewport={initialViewport}
      >
        <Background color="#333" gap={12} />
        <Controls className="" />
        <Panel position="top-right">
          <Button onClick={onLayout} variant="outline" size="sm">
            <LuLayoutTemplate className="mr-2 h-4 w-4" />
            Align
          </Button>
        </Panel>
      </ReactFlow>
    </div>
  );
}

function JsonNode({ data, selected }: { data: any; selected?: boolean }) {
  return (
    <div className="text-left h-full flex flex-col">
      <NodeResizer
        minWidth={200}
        minHeight={100}
        isVisible={selected}
        lineClassName="border-blue-400"
        handleClassName="h-3 w-3 bg-blue-400 border-none rounded"
      />
      <Handle type="target" position={Position.Top} id="in" />

      <h3 className="text-base mb-1.5">{data.label}</h3>

      <div className="nodrag bg-[#111827] p-2 rounded-md overflow-y-auto text-xs flex-1">
        <JsonView
          data={data.json}
          style={darkStyles}
          shouldExpandNode={collapseAllNested}
        />
      </div>

      <Handle type="source" position={Position.Bottom} id="out" />
    </div>
  );
}
