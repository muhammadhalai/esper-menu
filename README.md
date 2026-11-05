# Esper Salon & Spa — service menu

Live page: **https://esper-spa.netlify.app/**

Hosted on Netlify, which redeploys automatically on every push to `main`.
Also mirrored at https://muhammadhalai.github.io/esper-menu/

## How this is put together

| File | What it is |
|---|---|
| `menu.json` | **The source of truth.** Every service, price, hook and description. |
| `esper-menu-src.html` | The page template: design, layout and booking logic. |
| `logo_datauri.txt` | The Esper logo, embedded so the page needs no image files. |
| `build.py` | Reads the three above and writes `index.html`. |
| `index.html` | The built page. **Never edit this by hand.** |

## To change a price or a service

Edit `menu.json`, then run:

    python3 build.py && cp esper-menu.html index.html

Commit and push. GitHub Pages redeploys within a minute.

## Notes

- Every service is written into `index.html` as real HTML, so the menu still reads
  correctly in document viewers and for search and AI crawlers that do not run scripts.
  JavaScript only adds the tabs, the cart and the WhatsApp message.
- Booking goes to WhatsApp on +255 798 711 888.
- Prices are in Tanzanian shillings.
