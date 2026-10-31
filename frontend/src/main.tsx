import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (prefersReduced) {
  document.documentElement.dataset.reducedMotion = "true";
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
