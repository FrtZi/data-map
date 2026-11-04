"""The links the map draws: dbt's lineage collapsed onto the nodes the map shows."""

from collections.abc import Collection, Mapping


def shown_links(parents: Mapping[str, Collection[str]], shown: Collection[str]) -> list[tuple[str, str]]:
    """Each shown node's nearest shown ancestors: the steps the map does not show (an intermediate model, a
    check, a parameter table) are walked through, so raw.orders → staging.orders__checked → staging.orders reads
    as one link from raw.orders to staging.orders."""
    links: set[tuple[str, str]] = set()
    for node in shown:
        waiting, seen = list(parents.get(node, ())), set()
        while waiting:
            parent = waiting.pop()
            if parent in seen:
                continue
            seen.add(parent)
            if parent in shown:
                links.add((parent, node))
            else:
                waiting.extend(parents.get(parent, ()))
    return sorted(links)
