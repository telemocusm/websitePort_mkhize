(() => {
  const dialog = document.createElement('dialog');
  dialog.className = 'drawing-dialog';
  dialog.setAttribute('aria-labelledby', 'collection-view-title');
  dialog.innerHTML = '<div class="dialog-top"><h2 id="collection-view-title"></h2><button type="button" class="close" aria-label="Close project drawing">×</button></div><div class="drawing-viewer"><img alt=""></div><div class="drawing-controls"><button type="button" data-direction="-1" aria-label="Previous drawing">← Previous</button><span class="sheet-counter" aria-live="polite"></span><button type="button" data-direction="1" aria-label="Next drawing">Next →</button><a target="_blank" rel="noopener">Open original PDF</a></div>';
  document.body.append(dialog);
  let projects, current, index, trigger;
  const image = dialog.querySelector('img');
  function show() {
    const sheet = current.drawings[index];
    dialog.querySelector('h2').textContent = `${current.title} / ${sheet.title}`;
    image.src = sheet.image;
    image.alt = sheet.title;
    dialog.querySelector('a').href = sheet.pdf;
    dialog.querySelector('.sheet-counter').textContent = `${index + 1} / ${current.drawings.length}`;
    dialog.querySelector('[data-direction="-1"]').disabled = index === 0;
    dialog.querySelector('[data-direction="1"]').disabled = index === current.drawings.length - 1;
  }
  const ready = fetch('projects.json').then(r => {
    if (!r.ok) throw new Error('Project list unavailable');
    return r.json();
  }).then(data => projects = data);
  document.querySelectorAll('[data-collection]').forEach(button => button.addEventListener('click', async () => {
    try {
      await ready;
      current = projects.find(p => p.id === button.dataset.collection);
      index = Number(button.dataset.sheet);
      trigger = button;
      show();
      dialog.showModal();
      document.body.classList.add('modal-open');
    } catch {
      const fallback = document.createElement('p');
      fallback.textContent = 'The drawing viewer is unavailable. Open the original PDF from the project files below.';
      button.after(fallback);
    }
  }));
  dialog.querySelector('.close').addEventListener('click', () => dialog.close());
  dialog.querySelectorAll('[data-direction]').forEach(button => button.addEventListener('click', () => {
    index += Number(button.dataset.direction); show();
  }));
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowRight' && index < current.drawings.length - 1) { index++; show(); }
    if (event.key === 'ArrowLeft' && index > 0) { index--; show(); }
  });
  dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); trigger?.focus(); });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
})();
