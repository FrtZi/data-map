// The demo page: the component on the example map, as a host would mount it (`npm run dev`, `npm run build`).
import { mount } from "svelte";
import Demo from "./Demo.svelte";

mount(Demo, { target: document.getElementById("demo")! });
