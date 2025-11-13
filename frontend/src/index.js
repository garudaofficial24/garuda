import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Suppress ResizeObserver errors (benign and doesn't affect functionality)
const resizeObserverLoopErrRe = /^[^(ResizeObserver loop limit exceeded)]/;
const resizeObserverErrRe = /^[^(ResizeObserver loop completed with undelivered notifications)]/;
const origError = window.console.error;
window.console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    (resizeObserverLoopErrRe.test(args[0]) || 
     resizeObserverErrRe.test(args[0]) ||
     args[0].includes('ResizeObserver'))
  ) {
    return;
  }
  origError.call(window.console, ...args);
};

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
