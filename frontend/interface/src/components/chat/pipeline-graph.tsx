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
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { JsonView, darkStyles } from "react-json-view-lite";
import "react-json-view-lite/dist/index.css";
import { Label } from "../ui/label";

interface PipelineGraphProps {
  policyId: string;
  resolverOutput: any;
  irOutput: any;
  validationWarnings: string[];
  batfishWarnings: { severity: string; message: string }[];
  configs: Record<string, string>;
}

export default function PipelineGraph({
  policyId,
  resolverOutput,
  irOutput,
  validationWarnings,
  batfishWarnings,
  configs,
}: PipelineGraphProps) {
  const nodeWidth = 280;

  const initialNodes = useMemo(
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
        position: { x: 40, y: 340 },
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
        id: "validation",
        position: { x: 40, y: 660 },
        data: {
          label: "Linter Analysis",
          json:
            validationWarnings.length > 0
              ? validationWarnings
              : ["No linter warnings"],
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: validationWarnings.length > 0 ? "#b45309" : "#065f46",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
      {
        id: "batfish",
        position: { x: 40, y: 1300 },
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
      {
        id: "configs",
        position: { x: 40, y: 980 },
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
    ],
    [resolverOutput, irOutput, validationWarnings, batfishWarnings, configs]
  );

  const initialEdges = [
    {
      id: "resolver-ir",
      source: "resolver",
      target: "ir",
      type: "smoothstep",
      animated: true,
      style: { stroke: "#60a5fa", strokeWidth: 2 },
    },
    {
      id: "ir-validation",
      source: "ir",
      target: "validation",
      type: "smoothstep",
      animated: true,
      style: { stroke: "#60a5fa", strokeWidth: 2 },
    },
    {
      id: "configs-batfish",
      source: "configs",
      target: "batfish",
      type: "smoothstep",
      animated: true,
      style: { stroke: "#60a5fa", strokeWidth: 2 },
    },
    {
      id: "validation-configs",
      source: "validation",
      target: "configs",
      type: "smoothstep",
      animated: true,
      style: { stroke: "#60a5fa", strokeWidth: 2 },
    },
  ];

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

  const nodeTypes = {
    jsonNode: JsonNode,
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
      >
        <Background color="#333" gap={12} />
        <Controls className="" />
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
        <JsonView data={data.json} style={darkStyles} />
      </div>

      <Handle type="source" position={Position.Bottom} id="out" />
    </div>
  );
}
