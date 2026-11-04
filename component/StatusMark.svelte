<!-- A node's or a column's status: its icon and, for readers, its word; the colour only doubles them. -->
<script lang="ts">
  import type { Status } from "./document";
  import { ICONS } from "./labels";

  let { status, name, words = false }: { status: Status; name: string; words?: boolean } = $props();
</script>

<span class="mark {status.toLowerCase()}"
  ><span aria-hidden="true">{ICONS[status]}</span>{#if words}
    {name}{:else}<span class="dm-hidden">{name}</span>{/if}</span
>

<style>
  .mark {
    display: inline-flex;
    gap: 0.3em; /* between the icon and its word */
    font-weight: normal;
  }
  .sound {
    color: var(--dm-sound);
  }
  .to_look_at {
    color: var(--dm-to-look-at);
  }
  .blocking {
    color: var(--dm-blocking);
  }
  .not_built {
    color: var(--dm-muted);
  }
  .dm-hidden {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
    white-space: nowrap;
  }
</style>
