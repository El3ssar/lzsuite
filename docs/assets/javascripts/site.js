/* Small progressive enhancements; all documentation remains usable without JS. */
(() => {
  function setup() {
    const install = document.querySelector('.lz-install');
    if (install && !install.dataset.ready) {
      install.dataset.ready = 'true';
      const code = install.querySelector('code');
      install.querySelectorAll('[data-command]').forEach(button => {
        button.addEventListener('click', () => {
          install.querySelectorAll('[data-command]').forEach(other => other.setAttribute('aria-pressed', String(other === button)));
          code.textContent = button.dataset.command;
        });
      });
      const copy = install.querySelector('.lz-copy');
      copy.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(code.textContent);
          copy.textContent = 'Copied';
          setTimeout(() => { copy.textContent = 'Copy'; }, 1500);
        } catch (_) { copy.textContent = 'Select & copy'; }
      });
    }
    const axis = document.querySelector('#sequence-axis');
    if (axis && !axis.dataset.ready) {
      axis.dataset.ready = 'true';
      const update = () => {
        const dims = [1000, 4, 3];
        const selected = Number(axis.value);
        const batch = dims.filter((_, index) => index !== selected);
        document.querySelector('#sequence-length').textContent = dims[selected].toLocaleString('en-US');
        document.querySelector('#sequence-count').textContent = batch.reduce((a, b) => a * b, 1).toLocaleString('en-US');
        document.querySelector('#result-shape').textContent = `(${batch.join(', ')})`;
      };
      axis.addEventListener('change', update);
      update();
    }
  }
  if (typeof document$ !== 'undefined') document$.subscribe(setup);
  else if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', setup);
  else setup();
})();
