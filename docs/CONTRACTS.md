# Contracts (Authoritative)

## Generation contract
- Generation = immutable snapshot lineage node
- parent_ids stores ancestry
- Exactly one generation per project may be active at a time

## Spec contract
- instrumental_specs: geometry-driving, required completeness rules
- non_instrumental_specs: appearance + materials, optional but tracked
- A spec snapshot belongs to a generation; never overwritten

## Geometry contract
Input:
- instrumental_specs only

Output:
- mesh_uri (e.g. glb)
- anchors_uri (json)
- bounds (json)
- geometry_hash (sha256 of canonicalized instrumental specs)

## AI contract
- AI never edits instrumental specs
- AI actions are logged in ai_actions:
  - mode: resolve | draft | merge
  - fields_modified: list of JSON paths touched
  - invoked_by: user id

## Export contract
- Multi-format exports create separate files and a single ZIP container
- Factory profile includes: mesh + anchors + tech pack + BOM + materials
- Supplier profile includes: BOM + materials + textures only
