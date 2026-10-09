# Siphuthando Mkhize — portfolio

A static portfolio built with HTML, JavaScript, and Tailwind CSS. The packaged
site includes the supplied drawing exports and downloadable project documents.

## Quick upload to Netlify

1. Extract `Siphuthando-Mkhize-Netlify-Ready.zip`.
2. Open https://app.netlify.com/drop and sign in.
3. Drag the extracted `site` folder into the upload area. Its `index.html` must
   be directly inside that folder.

This archive contains the finished website. No build command is needed for
the manual upload.

## Edit the full project

Extract `Siphuthando-Mkhize-Portfolio-Source.zip` and open its project folder.

- Page content: `dist/index.html`
- Tailwind source styles: `src/styles.css`
- Interactions: `dist/script.js`
- Drawing images: `dist/assets/`
- Downloadable project files: `dist/documents/`

With Node.js installed, run:

```sh
npm ci
npm run build
npm run dev
```

Open http://127.0.0.1:4173 for the local preview.
Run `npm run build` after changing HTML or styles. `npm run watch:css`
rebuilds styles automatically while editing.

## Connect a repository to Netlify

Upload the full project to your own repository, then import it into Netlify.
The included `netlify.toml` sets:

- Build command: `npm run build`
- Publish directory: `dist`

The source archive does not include dependencies or a previous host's account
configuration. Install dependencies with `npm ci`.

Netlify documentation:
- https://docs.netlify.com/manage/projects/add-new-project/
- https://docs.netlify.com/build/configure-builds/overview/
# websitePort_mkhize
