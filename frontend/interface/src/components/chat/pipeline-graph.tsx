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
  configs: Record<string, string>;
}

export default function PipelineGraph({
  policyId,
  resolverOutput,
  irOutput,
  validationWarnings,
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
        position: { x: 240, y: 660 },
        data: {
          label: "Validation Warnings",
          json: validationWarnings,
        },
        style: {
          width: nodeWidth,
          padding: 10,
          borderRadius: 8,
          background: validationWarnings.length > 0 ? "#b45309" : "#1f2937",
          color: "#fff",
          border: "1px solid #374151",
        },
        type: "jsonNode",
      },
      {
        id: "configs",
        position: { x: 40, y: 850 },
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
    [resolverOutput, irOutput, validationWarnings, configs]
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
      id: "ir-configs",
      source: "ir",
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

function JsonNode({ data }: { data: any }) {
  return (
    <div className="text-left">
      <Handle type="target" position={Position.Top} id="in" />

      <h3 className="text-base mb-1.5">{data.label}</h3>

      <div className="nodrag bg-[#111827] p-2 rounded-md max-h-48 overflow-y-auto text-xs">
        <JsonView data={data.json} style={darkStyles} />
      </div>

      <Handle type="source" position={Position.Bottom} id="out" />
    </div>
  );
}
