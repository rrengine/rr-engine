# Next Engineering Steps (Ordered)

1) Geometry integration (deterministic)
   - geometry_assets table + model
   - geometry build after generation
   - persist geometry outputs

2) Import endpoint
   - create generation source=import
   - attach imported geometry_assets
   - defer validation until regenerate/export

3) Export engine + factory handoff
   - profile-based export builder
   - generate folder structure
   - zip packaging
