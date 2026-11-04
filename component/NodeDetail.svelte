<!-- The picked node's detail: its key figures, then each column with what it holds, its status and what the host
     found on it. -->
<script lang="ts">
  import type { Node, Status } from "./document";
  import type { Labels } from "./labels";
  import StatusMark from "./StatusMark.svelte";

  let { node, status, labels, locale }: { node: Node; status: Status; labels: Labels; locale: string } = $props();
  const shown = (value: number | string) => (typeof value === "number" ? value.toLocaleString(locale) : value);
</script>

<h3>{node.name} <StatusMark {status} name={labels.statuses[status]} words={true} /></h3>
<p class="muted">
  <code>{node.key}</code>{#if node.description}
    · {node.description}{/if}
</p>
{#if node.status_code === "NOT_BUILT"}
  <p class="muted">{labels.notBuilt}</p>
{:else}
  {#if node.figures?.length}
    <dl class="tiles">
      {#each node.figures as figure (figure.label)}
        <div>
          <dt>{figure.label}</dt>
          <dd class="num">{shown(figure.value)}</dd>
        </div>
      {/each}
    </dl>
  {/if}
  {#if node.columns?.length}
    <table class="columns">
      <colgroup><col class="c1" /><col /><col class="c3" /></colgroup>
      <thead><tr><th>{labels.column}</th><th>{labels.holds}</th><th>{labels.status}</th></tr></thead>
      <tbody>
        {#each node.columns as column (column.column_name)}
          {@const columnStatus = column.status_code ?? "SOUND"}
          <tr>
            <td><code title={column.data_type ?? undefined}>{column.column_name}</code></td>
            <td
              >{#if column.description}{column.description}{:else}<span class="muted">{labels.noDefinition}</span
                >{/if}</td
            >
            <td>
              <StatusMark status={columnStatus} name={labels.statuses[columnStatus]} words={true} />
              {#each column.notes ?? [] as note (note)}<br /><span class="muted">{note}</span>{/each}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
{/if}

<style>
  .muted {
    color: var(--dm-muted);
  }
  .columns {
    width: 100%;
    table-layout: fixed; /* the same widths from one node to the next */
    border-collapse: collapse;
  }
  th,
  td {
    padding: 4px 8px 4px 0;
    text-align: left;
    vertical-align: top;
  }
  .c1 {
    width: 26%;
  }
  .c3 {
    width: 22%;
  }
  code {
    overflow-wrap: anywhere;
  }
  h3 {
    margin: 12px 0 8px;
    font-size: 0.9375rem;
  }
  .tiles {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 8px;
    margin: 0 0 8px;
  }
  .tiles div {
    border: 1px solid var(--dm-rule);
    border-radius: 8px;
    padding: 8px 10px;
  }
  dt {
    color: var(--dm-muted);
    font-size: 0.75rem;
  }
  dd {
    margin: 2px 0 0;
    font-variant-numeric: tabular-nums;
  }
</style>
