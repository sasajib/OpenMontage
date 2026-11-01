---
name: documentary-evidence-visuals
description: Use when choosing documentary archive or stock visuals.
category: video-production
---

# Documentary evidence visuals

Documentary visuals are evidence. Use real sources first, and generate only images that show no people and make no factual claim.

- Real people: licensed photographs only (Wikimedia Commons CC or public domain), with on-screen credit. Never generate an image that depicts a real person.
- Headlines and newspapers: re-set from verified real headlines, showing publication and date. Never use scanned copyrighted pages.
- Website captures: real Wayback Machine captures in a period browser frame, with the archive URL visible.
- Numbers and claims on screen must trace to the research brief's sources.
- Generated stills: only textures and unpeopled atmosphere (desks, server racks, streets, paper stacks), with period-accurate props. Sample one frame before a batch (see `runpod-serverless-endpoints`).
- Keep the signature graphic device scarce (two beats at most).
- Every beat, including the closing and coda, needs real imagery (a licensed plate, Wayback capture, or Commons photo). A plain colour background reads as AI slop. The user rejected a closing that was "just background color which made the video ai slop". Cut between beats with crossfades, not dips to black.
- Avoid stock "handshake" footage, glossy UI mockups, and logos used as decoration.
- Before promising a stock source, check `.env`. In this workspace `PEXELS_API_KEY` and `PIXABAY_API_KEY` were empty, so Pexels and Pixabay images were unavailable; Unsplash worked. Pixabay Music search needs no key. Tell the user which sources are live before building the plan.
