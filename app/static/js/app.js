/* ============================================================
   GirlHub — Main JavaScript
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

    // ── Loading overlay ──────────────────────────────────
    const loader = document.getElementById('page-loader');
    if (loader) {
        window.addEventListener('load', () => {
            loader.classList.add('opacity-0');
            setTimeout(() => loader.remove(), 400);
        });
    }

    // ── Confirm dialogs for delete forms ─────────────────
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', e => {
            if (!confirm(form.dataset.confirm || 'Are you sure?')) {
                e.preventDefault();
            }
        });
    });

    // ── Smooth scroll for anchor links ───────────────────
    document.querySelectorAll('a[href^="#"]').forEach(a => {
        a.addEventListener('click', e => {
            const target = document.querySelector(a.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ── Intersection Observer fade-in ────────────────────
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.observe-fade').forEach(el => observer.observe(el));

    // ── Generic image preview ────────────────────────────
    document.querySelectorAll('[data-preview]').forEach(input => {
        input.addEventListener('change', () => {
            const container = document.getElementById(input.dataset.preview);
            if (!container) return;
            container.innerHTML = '';
            [...input.files].forEach(file => {
                if (!file.type.startsWith('image/')) return;
                const reader = new FileReader();
                reader.onload = e => {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'w-20 h-20 rounded-xl object-cover border-2 border-primary-300';
                    container.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    });

    // ── Number counter animation ─────────────────────────
    document.querySelectorAll('[data-count]').forEach(el => {
        const target = parseFloat(el.dataset.count);
        const duration = 1200;
        const start = performance.now();
        const prefix = el.dataset.prefix || '';
        const suffix = el.dataset.suffix || '';
        const decimals = el.dataset.decimals ? parseInt(el.dataset.decimals) : 0;

        function animate(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
            const current = target * eased;
            el.textContent = prefix + current.toFixed(decimals) + suffix;
            if (progress < 1) requestAnimationFrame(animate);
        }

        requestAnimationFrame(animate);
    });

    // ── Toast programmatic helper ────────────────────────
    window.showToast = function(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const icons = {
            success: 'fa-circle-check',
            danger: 'fa-circle-xmark',
            warning: 'fa-triangle-exclamation',
            info: 'fa-circle-info'
        };
        const colors = {
            success: 'bg-emerald-500',
            danger: 'bg-red-500',
            warning: 'bg-amber-500',
            info: 'bg-blue-500'
        };

        const toast = document.createElement('div');
        toast.className = `toast-enter flex items-start gap-3 p-4 rounded-xl shadow-lg text-white ${colors[type] || colors.info}`;
        toast.innerHTML = `
            <i class="fa-solid ${icons[type] || icons.info} mt-0.5 text-lg"></i>
            <span class="flex-1 text-sm font-medium">${message}</span>
            <button onclick="this.parentElement.classList.replace('toast-enter','toast-exit');setTimeout(()=>this.parentElement.remove(),300)"
                class="hover:opacity-70 transition"><i class="fa-solid fa-xmark"></i></button>
        `;
        container.appendChild(toast);
        setTimeout(() => {
            toast.classList.replace('toast-enter', 'toast-exit');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    };

});
