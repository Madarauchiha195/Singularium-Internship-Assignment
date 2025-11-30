import React, { useRef, useEffect } from "react";
import { Network } from "vis-network/standalone";

export default function Graph({ tasks = [], cycles = [] }) {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;

    // build nodes and edges
    const nodes = tasks.map((t) => ({
      id: t.id,
      label: `${t.title || t.id}\n(${t.id})`,
      title: t.explanation || "",
      value: t.score || 0
    }));

    const idSet = new Set(tasks.map((t) => t.id));
    const edges = [];
    tasks.forEach((t) => {
      (t.dependencies || []).forEach((dep) => {
        if (idSet.has(dep)) {
          edges.push({
            from: dep,
            to: t.id,
            arrows: "to",
            physics: false,
            smooth: { enabled: true, type: "curvedCW", roundness: 0.15 }
          });
        }
      });
    });

    // highlight cycle nodes
    const cycleNodes = new Set();
    (cycles || []).forEach((c) => c.forEach((n) => cycleNodes.add(n)));

    const visNodes = nodes.map((n) => {
      const urgencySubscore = (tasks.find((t) => t.id === n.id)?.subscores?.urgency) ?? 0;
      // color by urgency
      let color = "#10b981"; // green
      if (urgencySubscore >= 1.0) color = "#ef4444"; // overdue/high - red
      else if (urgencySubscore >= 0.7) color = "#f59e0b"; // orange
      else color = "#10b981"; // green

      return {
        id: n.id,
        label: n.label,
        title: n.title,
        color: cycleNodes.has(n.id) ? { background: "#ffd6d6", border: "#ff0000" } : { background: color },
        shape: "box",
        borderWidth: cycleNodes.has(n.id) ? 3 : 1
      };
    });

    const data = { nodes: visNodes, edges };
    const options = {
      nodes: { font: { multi: "html" }, margin: 8 },
      edges: { color: { color: "#333" } },
      layout: { improvedLayout: true },
      physics: { stabilization: true, barnesHut: { gravitationalConstant: -2000 } },
      interaction: { hover: true, multiselect: false, navigationButtons: true }
    };

    const network = new Network(ref.current, data, options);

    network.on("click", function (params) {
      if (params.nodes.length) {
        const nodeId = params.nodes[0];
        const t = tasks.find((x) => x.id === nodeId);
        if (t) {
          // show quick info
          alert(`${t.title || t.id}\nScore: ${t.score ?? "—"}\n${t.explanation}`);
        }
      }
    });

    return () => network.destroy();
  }, [tasks, cycles]);

  return <div ref={ref} style={{ height: 360, borderRadius: 8, border: "1px solid #e6e9ef" }} />;
}
