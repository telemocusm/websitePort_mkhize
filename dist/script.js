const study = document.getElementById('study-dialog');
const trigger = document.getElementById('open-study');
trigger.addEventListener('click', () => {
  study.showModal();
  document.body.classList.add('modal-open');
});
study.querySelector('.close').addEventListener('click', () => study.close());
study.addEventListener('click', event => {
  if (event.target !== study) return;
  const box = study.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) study.close();
});
study.addEventListener('close', () => {
  document.body.classList.remove('modal-open');
  trigger.focus();
});
const filters = document.querySelectorAll('.matrix-filters button');
const stages = document.querySelectorAll('.matrix-step');
filters.forEach(button => button.addEventListener('click', () => {
  const phase = button.dataset.filter;
  filters.forEach(filter => filter.setAttribute('aria-pressed', String(filter === button)));
  let count = 0;
  stages.forEach(stage => {
    stage.hidden = phase !== 'all' && stage.dataset.phase !== phase;
    if (!stage.hidden) count++;
  });
  document.querySelector('.matrix-count').textContent = `Showing ${count} stages`;
}));
const drawingDialog = document.getElementById('drawing-dialog');
const drawingImage = document.getElementById('drawing-image');
const drawingFiles = {
  '1': { title: 'Section & reinforcement', pdf: 'slab-section.pdf', alt: 'Reinforced slab section between grids 3 and 4' },
  '2': { title: 'Frame elevation', pdf: 'slab-elevation.pdf', alt: 'Concrete frame elevation between grids 2 and 1' },
  '3': { title: 'Reinforced model', pdf: 'slab-model.pdf', alt: 'Revit 3D view of slab reinforcement, concrete frame and footings' }
};
let selectedProject = 1;
let drawingTrigger;
function showDrawing(index) {
  const drawing = drawingFiles[index];
  drawingImage.src = `assets/slab-${index}.png`;
  drawingImage.alt = drawing.alt;
  document.getElementById('drawing-title').textContent = `Project ${selectedProject} / ${drawing.title}`;
  document.getElementById('drawing-pdf').href = `documents/${drawing.pdf}`;

  drawingDialog.querySelectorAll('[data-gallery]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.gallery === index)));
}
function openDrawing(index, project, triggerElement) {
  selectedProject = project;
  drawingTrigger = triggerElement;
  showDrawing(index);
  drawingDialog.showModal();
  document.body.classList.add('modal-open');
}
document.querySelectorAll('[data-drawing]').forEach(button => button.addEventListener('click', () => openDrawing(button.dataset.drawing, 1, button)));
document.getElementById('open-project-two')?.addEventListener('click', event => openDrawing('3', 2, event.currentTarget));
document.querySelector('[data-project-two-image]')?.addEventListener('click', event => openDrawing('3', 2, event.currentTarget));
drawingDialog.querySelectorAll('[data-gallery]').forEach(button => button.addEventListener('click', () => showDrawing(button.dataset.gallery)));
drawingDialog.querySelector('.close').addEventListener('click', () => drawingDialog.close());
drawingDialog.addEventListener('close', () => {
  document.body.classList.remove('modal-open');
  drawingTrigger?.focus();
});
drawingDialog.addEventListener('click', event => {
  if (event.target !== drawingDialog) return;
  const box = drawingDialog.getBoundingClientRect();
  if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) drawingDialog.close();
});
