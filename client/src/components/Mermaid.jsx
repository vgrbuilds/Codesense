import React, { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
  }
});

export default function Mermaid({ chart }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (!chart || !containerRef.current) return;
    
    // Clear previous output
    containerRef.current.innerHTML = '<div class="loading-diagram">Rendering diagram...</div>';

    // Remove any markdown fencing if the model returned it (e.g. ```mermaid ... ```)
    let cleanChart = chart.trim();
    if (cleanChart.startsWith('```mermaid')) {
      cleanChart = cleanChart.substring(10);
    }
    if (cleanChart.startsWith('```')) {
      cleanChart = cleanChart.substring(3);
    }
    if (cleanChart.endsWith('```')) {
      cleanChart = cleanChart.substring(0, cleanChart.length - 3);
    }
    cleanChart = cleanChart.trim();

    const id = `mermaid-diag-${Math.floor(Math.random() * 1000000)}`;
    
    // Render the chart
    mermaid.render(id, cleanChart)
      .then(({ svg }) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      })
      .catch((err) => {
        console.error("Mermaid parsing error:", err);
        // Clear broken element that mermaid adds to body
        const badEl = document.getElementById(id);
        if (badEl) badEl.remove();
        
        if (containerRef.current) {
          containerRef.current.innerHTML = `
            <div class="mermaid-error">
              <p>⚠️ Failed to render diagram. Raw markup:</p>
              <pre>${cleanChart}</pre>
            </div>
          `;
        }
      });
  }, [chart]);

  return (
    <div className="mermaid-wrapper" ref={containerRef}>
      <div className="loading-diagram">Loading diagram...</div>
    </div>
  );
}
