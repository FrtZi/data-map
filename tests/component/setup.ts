// What jsdom lacks and Svelte Flow reads (the map): jsdom lays nothing out, so every element is
// given a width and a height, sizes are observed at once, and the media queries and matrices answer something.
class ImmediateResizeObserver {
  constructor(private readonly callback: ResizeObserverCallback) {}
  observe(target: Element) {
    this.callback([{ target, contentRect: target.getBoundingClientRect() } as ResizeObserverEntry], this);
  }
  unobserve() {}
  disconnect() {}
}

class IdentityMatrix {
  m22 = 1; // Svelte Flow reads the zoom from the transform's scale
}

const LAID_OUT = { clientWidth: 1000, clientHeight: 600, offsetWidth: 1000, offsetHeight: 600 };

globalThis.ResizeObserver ??= ImmediateResizeObserver as unknown as typeof ResizeObserver;
globalThis.DOMMatrixReadOnly ??= IdentityMatrix as unknown as typeof DOMMatrixReadOnly;
window.matchMedia ??= (query: string) =>
  ({ matches: false, media: query, addEventListener() {}, removeEventListener() {} }) as unknown as MediaQueryList;
for (const [name, value] of Object.entries(LAID_OUT)) {
  Object.defineProperty(HTMLElement.prototype, name, { configurable: true, get: () => value });
}
