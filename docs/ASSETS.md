# Visual asset provenance

`apps/web/public/images/hero-concept.webp` is an AI-generated photographic concept
created with the built-in image generation tool for this prototype on 21 October
2026. The PNG source is kept alongside it. The WebP is the optimized runtime asset.
It is labeled as concept artwork in the homepage and is never assigned to a
supplier's listing.

Generation prompt:

> Use case: ads-marketing. Asset type: wide website hero photographic concept
> artwork. Understated premium luxury automotive editorial photograph for an
> independent car rental marketplace design concept. A dark graphite luxury grand
> touring coupe parked on a stone courtyard beside sculptural warm limestone
> architecture in a desert destination, wide three-quarter front angle, pristine
> metallic surfaces, authentic materials and believable proportions. Wide landscape
> 3:2 composition. Car in right-center with generous deep dark forest-green negative
> space toward left and top. Cinematic early evening warm edge lighting, deep
> green-black shadows, restrained champagne highlights, sophisticated automotive
> print campaign look. No people, badges, manufacturer logos, text, number plates
> with writing, or watermarks. Aspirational concept artwork, not a specific real
> supplier vehicle.

`components/vehicle.tsx` contains original SVG vehicle illustrations. They are
explicitly labeled when used instead of supplier photography. They are generic
visuals and do not verify the pictured listing's actual appearance.

Supplier uploads are decoded and re-encoded by the API and remain demonstration
runtime data, excluded from source control. No production LavishCars photographs,
customer reviews or supplier records were copied into this application.
