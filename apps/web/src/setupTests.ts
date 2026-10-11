import '@testing-library/jest-dom/vitest';

// Polyfill ResizeObserver for headless test environments
if (typeof globalThis.ResizeObserver === 'undefined') {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
