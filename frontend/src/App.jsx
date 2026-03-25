// import { useState, useEffect, useCallback } from "react";
// import ReactFlow, { 
//   Background, Controls, MiniMap,
//   useNodesState, useEdgesState
// } from "reactflow";
// import "reactflow/dist/style.css";
// import axios from "axios";

// const API = "http://localhost:8000";

// const nodeColors = {
//   SalesOrder: "#4f46e5",
//   SalesOrderItem: "#7c3aed",
//   DeliveryItem: "#0891b2",
//   BillingItem: "#059669",
//   Customer: "#d97706",
//   Product: "#dc2626",
//   Plant: "#65a30d",
//   JournalEntry: "#c026d3",
//   Payment: "#0284c7",
// };

// export default function App() {
//   const [nodes, setNodes, onNodesChange] = useNodesState([]);
//   const [edges, setEdges, onEdgesChange] = useEdgesState([]);
//   const [question, setQuestion] = useState("");
//   const [messages, setMessages] = useState([
//     { role: "bot", text: "Hello! Ask me anything about the SAP Order-to-Cash dataset." }
//   ]);
//   const [loading, setLoading] = useState(false);
//   const [selectedNode, setSelectedNode] = useState(null);

//   useEffect(() => {
//     axios.get(`${API}/graph`).then((res) => {
//       const data = res.data;

//       const rfNodes = data.nodes.slice(0, 100).map((n, i) => ({
//         id: n.id,
//         data: { label: n.label, type: n.type, meta: n.data },
//         position: { 
//           x: (i % 10) * 180 + Math.random() * 50, 
//           y: Math.floor(i / 10) * 120 + Math.random() * 50 
//         },
//         style: {
//           background: nodeColors[n.type] || "#6b7280",
//           color: "white",
//           border: "none",
//           borderRadius: "8px",
//           padding: "8px",
//           fontSize: "11px",
//           width: 140,
//         },
//       }));

//       const rfEdges = data.edges.slice(0, 200).map((e, i) => ({
//         id: `e${i}`,
//         source: e.source,
//         target: e.target,
//         label: e.relation,
//         style: { stroke: "#94a3b8" },
//         labelStyle: { fontSize: 9, fill: "#94a3b8" },
//         animated: true,
//       }));

//       setNodes(rfNodes);
//       setEdges(rfEdges);
//     });
//   }, []);

  // const sendMessage = async () => {
  //   if (!question.trim()) return;
  //   const q = question;
  //   setQuestion("");
  //   setMessages((prev) => [...prev, { role: "user", text: q }]);
  //   setLoading(true);

  //   try {
  //     const res = await axios.post(`${API}/query`, { question: q });
  //     const answer = res.data.answer;
  //     const data = res.data.data;

  //     let botMsg = answer;
  //     if (data && Array.isArray(data) && data.length > 0) {
  //       botMsg += "\n\n📊 Data:\n" + JSON.stringify(data.slice(0, 5), null, 2);
  //     }
  //     setMessages((prev) => [...prev, { role: "bot", text: botMsg }]);
  //   } catch {
  //     setMessages((prev) => [...prev, { role: "bot", text: "Error connecting to backend." }]);
  //   }
  //   setLoading(false);
  // };


//   const sendMessage = async () => {
//   if (!question.trim()) return;

//   const q = question;

//   console.log("🚀 Sending request:", q); // ✅ DEBUG

//   setQuestion("");
//   setMessages((prev) => [...prev, { role: "user", text: q }]);
//   setLoading(true);

//   try {
//     const res = await axios.post("http://localhost:8000/query", {
//       question: q,
//     });

//     console.log("✅ Response:", res.data); // ✅ DEBUG

//     const answer = res.data.answer;
//     const data = res.data.data;

//     let botMsg = answer;

//     if (data && Array.isArray(data) && data.length > 0) {
//       botMsg += "\n\n📊 Data:\n" + JSON.stringify(data.slice(0, 5), null, 2);
//     }

//     setMessages((prev) => [...prev, { role: "bot", text: botMsg }]);

//   } catch (err) {
//     console.error("❌ Error:", err);
//     setMessages((prev) => [
//       ...prev,
//       { role: "bot", text: "Error connecting to backend." },
//     ]);
//   }

//   setLoading(false);
// };

//   return (
//     <div style={{ display: "flex", height: "100vh", background: "#0f172a", color: "white", fontFamily: "sans-serif" }}>
      
//       {/* Left: Graph */}
//       <div style={{ flex: 1, position: "relative" }}>
//         <div style={{ padding: "12px 16px", background: "#1e293b", borderBottom: "1px solid #334155" }}>
//           <h2 style={{ margin: 0, fontSize: 16 }}>🔗 SAP Order-to-Cash Graph</h2>
//           <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>498 nodes · 90 edges</p>
//         </div>

//         {/* Legend */}
//         <div style={{ position: "absolute", bottom: 10, left: 10, zIndex: 10, background: "#1e293b", padding: 10, borderRadius: 8, fontSize: 11 }}>
//           {Object.entries(nodeColors).map(([type, color]) => (
//             <div key={type} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
//               <div style={{ width: 12, height: 12, background: color, borderRadius: 3 }} />
//               <span>{type}</span>
//             </div>
//           ))}
//         </div>

//         <ReactFlow
//           nodes={nodes}
//           edges={edges}
//           onNodesChange={onNodesChange}
//           onEdgesChange={onEdgesChange}
//           onNodeClick={(_, node) => setSelectedNode(node.data)}
//           fitView
//         >
//           <Background color="#334155" gap={20} />
//           <Controls />
//           <MiniMap nodeColor={(n) => nodeColors[n.data?.type] || "#6b7280"} style={{ background: "#1e293b" }} />
//         </ReactFlow>

//         {/* Node detail panel */}
//         {selectedNode && (
//           <div style={{ position: "absolute", top: 60, right: 10, background: "#1e293b", border: "1px solid #334155", borderRadius: 8, padding: 12, width: 220, zIndex: 10, fontSize: 11, maxHeight: 300, overflowY: "auto" }}>
//             <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
//               <b style={{ color: nodeColors[selectedNode.type] }}>{selectedNode.type}</b>
//               <span style={{ cursor: "pointer", color: "#94a3b8" }} onClick={() => setSelectedNode(null)}>✕</span>
//             </div>
//             {Object.entries(selectedNode.meta || {}).slice(0, 10).map(([k, v]) => (
//               <div key={k} style={{ marginBottom: 4 }}>
//                 <span style={{ color: "#94a3b8" }}>{k}: </span>
//                 <span>{String(v).slice(0, 30)}</span>
//               </div>
//             ))}
//           </div>
//         )}
//       </div>

//       {/* Right: Chat */}
//       <div style={{ width: 380, display: "flex", flexDirection: "column", background: "#1e293b", borderLeft: "1px solid #334155" }}>
//         <div style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>
//           <h2 style={{ margin: 0, fontSize: 16 }}>💬 Query Interface</h2>
//           <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>Ask questions about your data</p>
//         </div>

//         {/* Messages */}
//         <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
//           {messages.map((m, i) => (
//             <div key={i} style={{
//               alignSelf: m.role === "user" ? "flex-end" : "flex-start",
//               background: m.role === "user" ? "#4f46e5" : "#0f172a",
//               padding: "10px 14px",
//               borderRadius: 12,
//               maxWidth: "85%",
//               fontSize: 13,
//               whiteSpace: "pre-wrap",
//               lineHeight: 1.5,
//             }}>
//               {m.text}
//             </div>
//           ))}
//           {loading && (
//             <div style={{ alignSelf: "flex-start", background: "#0f172a", padding: "10px 14px", borderRadius: 12, fontSize: 13, color: "#94a3b8" }}>
//               Thinking...
//             </div>
//           )}
//         </div>

//         {/* Example queries */}
//         <div style={{ padding: "8px 16px", borderTop: "1px solid #334155" }}>
//           <p style={{ margin: "0 0 6px", fontSize: 11, color: "#64748b" }}>Try asking:</p>
//           {[
//             "Which products have the most billing documents?",
//             "Show me incomplete sales orders",
//             "How many deliveries are there?",
//           ].map((q) => (
//             <div key={q} onClick={() => setQuestion(q)}
//               style={{ fontSize: 11, color: "#94a3b8", cursor: "pointer", marginBottom: 4, padding: "4px 8px", background: "#0f172a", borderRadius: 6 }}>
//               {q}
//             </div>
//           ))}
//         </div>

//         {/* Input */}
//         <div style={{ padding: 16, borderTop: "1px solid #334155", display: "flex", gap: 8 }}>
//           <input
//             value={question}
//             onChange={(e) => setQuestion(e.target.value)}
//             onKeyDown={(e) => e.key === "Enter" && sendMessage()}
//             placeholder="Ask about the dataset..."
//             style={{ flex: 1, padding: "10px 12px", borderRadius: 8, border: "1px solid #334155", background: "#0f172a", color: "white", fontSize: 13, outline: "none" }}
//           />
//           <button onClick={sendMessage} disabled={loading}
//             style={{ padding: "10px 16px", background: "#4f46e5", color: "white", border: "none", borderRadius: 8, cursor: "pointer", fontSize: 13 }}>
//             Send
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }














































// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from './assets/vite.svg'
// import heroImg from './assets/hero.png'
// import './App.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <>
//       <section id="center">
//         <div className="hero">
//           <img src={heroImg} className="base" width="170" height="179" alt="" />
//           <img src={reactLogo} className="framework" alt="React logo" />
//           <img src={viteLogo} className="vite" alt="Vite logo" />
//         </div>
//         <div>
//           <h1>Get started</h1>
//           <p>
//             Edit <code>src/App.jsx</code> and save to test <code>HMR</code>
//           </p>
//         </div>
//         <button
//           className="counter"
//           onClick={() => setCount((count) => count + 1)}
//         >
//           Count is {count}
//         </button>
//       </section>

//       <div className="ticks"></div>

//       <section id="next-steps">
//         <div id="docs">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#documentation-icon"></use>
//           </svg>
//           <h2>Documentation</h2>
//           <p>Your questions, answered</p>
//           <ul>
//             <li>
//               <a href="https://vite.dev/" target="_blank">
//                 <img className="logo" src={viteLogo} alt="" />
//                 Explore Vite
//               </a>
//             </li>
//             <li>
//               <a href="https://react.dev/" target="_blank">
//                 <img className="button-icon" src={reactLogo} alt="" />
//                 Learn more
//               </a>
//             </li>
//           </ul>
//         </div>
//         <div id="social">
//           <svg className="icon" role="presentation" aria-hidden="true">
//             <use href="/icons.svg#social-icon"></use>
//           </svg>
//           <h2>Connect with us</h2>
//           <p>Join the Vite community</p>
//           <ul>
//             <li>
//               <a href="https://github.com/vitejs/vite" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#github-icon"></use>
//                 </svg>
//                 GitHub
//               </a>
//             </li>
//             <li>
//               <a href="https://chat.vite.dev/" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#discord-icon"></use>
//                 </svg>
//                 Discord
//               </a>
//             </li>
//             <li>
//               <a href="https://x.com/vite_js" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#x-icon"></use>
//                 </svg>
//                 X.com
//               </a>
//             </li>
//             <li>
//               <a href="https://bsky.app/profile/vite.dev" target="_blank">
//                 <svg
//                   className="button-icon"
//                   role="presentation"
//                   aria-hidden="true"
//                 >
//                   <use href="/icons.svg#bluesky-icon"></use>
//                 </svg>
//                 Bluesky
//               </a>
//             </li>
//           </ul>
//         </div>
//       </section>

//       <div className="ticks"></div>
//       <section id="spacer"></section>
//     </>
//   )
// }

// export default App




























import { useState, useEffect } from "react";
import ReactFlow, {
  Background, Controls, MiniMap,
  useNodesState, useEdgesState
} from "reactflow";
import "reactflow/dist/style.css";
import axios from "axios";

// ✅ YOUR DEPLOYED BACKEND URL
const API = "https://dodge-graph-msi1.onrender.com";

const nodeColors = {
  SalesOrder: "#4f46e5",
  SalesOrderItem: "#7c3aed",
  DeliveryItem: "#0891b2",
  BillingItem: "#059669",
  Customer: "#d97706",
  Product: "#dc2626",
  Plant: "#65a30d",
  JournalEntry: "#c026d3",
  Payment: "#0284c7",
};

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: "Hello! Ask me anything about the SAP Order-to-Cash dataset." }
  ]);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);

  // ✅ GRAPH FETCH
  useEffect(() => {
    axios.get(`${API}/graph`).then((res) => {
      const data = res.data;

      const rfNodes = data.nodes.slice(0, 100).map((n, i) => ({
        id: n.id,
        data: { label: n.label, type: n.type, meta: n.data },
        position: {
          x: (i % 10) * 180 + Math.random() * 50,
          y: Math.floor(i / 10) * 120 + Math.random() * 50
        },
        style: {
          background: nodeColors[n.type] || "#6b7280",
          color: "white",
          border: "none",
          borderRadius: "8px",
          padding: "8px",
          fontSize: "11px",
          width: 140,
        },
      }));

      const rfEdges = data.edges.slice(0, 200).map((e, i) => ({
        id: `e${i}`,
        source: e.source,
        target: e.target,
        label: e.relation,
        style: { stroke: "#94a3b8" },
        labelStyle: { fontSize: 9, fill: "#94a3b8" },
        animated: true,
      }));

      setNodes(rfNodes);
      setEdges(rfEdges);
    });
  }, []);

  // ✅ QUERY FUNCTION (FIXED)
  const sendMessage = async () => {
    if (!question.trim()) return;

    const q = question;
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", text: q }]);
    setLoading(true);

    try {
      const res = await axios.post(`${API}/query`, {
        question: q,
      });

      const answer = res.data.answer;
      const data = res.data.data;

      let botMsg = answer;

      if (data && Array.isArray(data) && data.length > 0) {
        botMsg += "\n\n📊 Data:\n" + JSON.stringify(data.slice(0, 5), null, 2);
      }

      setMessages((prev) => [...prev, { role: "bot", text: botMsg }]);

    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Error connecting to backend." },
      ]);
    }

    setLoading(false);
  };

  return (
    <div style={{ display: "flex", height: "100vh", background: "#0f172a", color: "white", fontFamily: "sans-serif" }}>

      {/* LEFT: GRAPH */}
      <div style={{ flex: 1, position: "relative" }}>
        <div style={{ padding: "12px 16px", background: "#1e293b", borderBottom: "1px solid #334155" }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>🔗 SAP Order-to-Cash Graph</h2>
          <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>498 nodes · 90 edges</p>
        </div>

        {/* Legend */}
        <div style={{ position: "absolute", bottom: 10, left: 10, zIndex: 10, background: "#1e293b", padding: 10, borderRadius: 8, fontSize: 11 }}>
          {Object.entries(nodeColors).map(([type, color]) => (
            <div key={type} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
              <div style={{ width: 12, height: 12, background: color, borderRadius: 3 }} />
              <span>{type}</span>
            </div>
          ))}
        </div>

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={(_, node) => setSelectedNode(node.data)}
          fitView
        >
          <Background color="#334155" gap={20} />
          <Controls />
          <MiniMap nodeColor={(n) => nodeColors[n.data?.type] || "#6b7280"} style={{ background: "#1e293b" }} />
        </ReactFlow>
      </div>

      {/* RIGHT: CHAT */}
      <div style={{ width: 380, display: "flex", flexDirection: "column", background: "#1e293b", borderLeft: "1px solid #334155" }}>
        <div style={{ padding: "12px 16px", borderBottom: "1px solid #334155" }}>
          <h2 style={{ margin: 0, fontSize: 16 }}>💬 Query Interface</h2>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: 16, display: "flex", flexDirection: "column", gap: 12 }}>
          {messages.map((m, i) => (
            <div key={i} style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "#4f46e5" : "#0f172a",
              padding: "10px 14px",
              borderRadius: 12,
              maxWidth: "85%",
              fontSize: 13,
              whiteSpace: "pre-wrap",
            }}>
              {m.text}
            </div>
          ))}
          {loading && <div>Thinking...</div>}
        </div>

        <div style={{ padding: 16, display: "flex", gap: 8 }}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask about the dataset..."
            style={{ flex: 1 }}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}