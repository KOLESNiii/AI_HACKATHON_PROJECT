# Retailer asset import (#19, Dev 2.7)

## Intent

The editor's library is mock data. A user should be able to paste a retailer link, or pick a
search result, and get a furniture item that is honest about its size: the retailer's
published dimensions lock the bounding box, and the item moves and audits like video
furniture. The issue requires that this reuses the existing reconstruction and normalisation
functions and keeps source, image and dimension provenance.

## Goals

- A product URL or search result becomes a `FurnitureAsset` through the #14 to #18 pipeline.
- Source URL, image, model and the published dimension text are retained.
- A missing or unreadable size requests a `"dimensions"` correction; it is never invented.
- IKEA is the working base: it publishes sizes, images and, for many products, 3D models.

## Non-goals

- No route and no `contracts/` change (needs team sign-off); no frontend change.
- No new dependency: no Draco decoder, no mesh decimator, no search API key.
- No broad segmentation or mesh-quality work on video furniture. The one quality change is
  in the shared normaliser (texture reduction before a file is refused).

## Approaches

1. **A separate catalog path** (download a model or image, normalise, build the asset by
   hand). Rejected: it repeats the storage, reuse, fallback and check rules of #16 to #18,
   which is the second pipeline the issue forbids.
2. **Always generate from the product image** (image, SAM 3 mask, SAM 3D). Rejected as the
   only path: it pays for and approximates a shape the retailer often publishes exactly.
   Kept as the fallback.
3. **Register the product as a one-view item in the registry** (chosen). The product image
   is the item's frame; the existing `segment_furniture`, `reconstruct_furniture`,
   `normalise_mesh` and `deliver_furniture` run unchanged. A retailer-published model enters
   through the existing `MeshProvider` boundary as the raw mesh, ahead of a generated one.

## Design

- `retailer.py`: `fetch_product` / `parse_product_page` read schema.org `Product` and
  `3DModel` JSON-LD, then meta tags, `<model-viewer>` and labelled page text, into a
  `RetailerProduct`. `search_ikea` returns search results. `fetch_public` refuses
  non-public addresses on every redirect hop and caps sizes.
- `catalog.py`: `import_product` registers the item under scene key `catalog:<scene_id>`
  with ID `cat-<hash of URL>`, runs the pipeline, relabels the delivered asset with the
  product's `source`, `product_url` and `price_gbp`, and stores a `CatalogImport` record.
  `RetailerModelProvider` yields the retailer's models best first; the importer asks for the
  next when one does not normalise. Published width and depth follow the delivered shape's
  axes.
- `import_product.py`: the CLI, with the same exit-code convention as the other tools.
- `normalisation.py`: textures step down to 768 px and 512 px when a file exceeds 3 MB.
  `PROVIDER_FRONT["retailer"] = "+z"`. `MeshRecord.provider` gains `"retailer"`.

Details, provenance tables and the live verification are in
`services/reconstruction/assets/README.md`.

## Left open

- A request model and route for the editor's link import (contracts sign-off, Dev 1/Dev 3).
- Draco decoding (IKEA sofas publish only Draco models) and live checks of other retailers.
- A live check of the paid image-to-mesh fallback on a product photo.
