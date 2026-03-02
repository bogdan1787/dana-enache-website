/**
 * blood.js — Animated blood drip effect (canvas-based, plug-and-play).
 * Homepage shows 4 drops; all other pages show 1.
 * Mark the homepage <body data-page="home"> to trigger more drops.
 */
(function () {
  const style = document.createElement('style');
  style.textContent = `
    .blood-drip-container {
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      pointer-events: none; z-index: 999999; overflow: hidden;
    }
  `;
  document.head.appendChild(style);

  const container = document.createElement('div');
  container.className = 'blood-drip-container';
  document.body.appendChild(container);

  const maxDrops = document.body.dataset.page === 'home' ? 4 : 1;
  const drops = [];

  class BloodDrop {
    constructor() {
      this.trail = document.createElement('canvas');
      Object.assign(this.trail.style, {
        position: 'absolute', top: '0', left: '0',
        width: '100%', height: '100%', pointerEvents: 'none',
      });
      this.trail.width  = window.innerWidth;
      this.trail.height = window.innerHeight;
      this.ctx = this.trail.getContext('2d');
      container.appendChild(this.trail);
      this.reset();
    }

    reset() {
      this.ctx.clearRect(0, 0, this.trail.width, this.trail.height);

      const sideWidth = window.innerWidth * 0.3;
      const left = Math.random() < 0.5;
      this.x = left
        ? 20 + Math.random() * sideWidth
        : window.innerWidth - (20 + Math.random() * sideWidth);
      this.y     = -30;
      this.lastY = this.y;

      this.baseSpeed = 0.3 + Math.random() * 0.4;
      this.speed     = this.baseSpeed;
      this.size      = 8 + Math.random() * 6;

      const sat   = 85 + Math.random() * 15;
      const light = 20 + Math.random() * 15;
      this.color      = `hsl(0,${sat}%,${light}%)`;
      this.darkColor  = `hsl(0,${sat}%,${light - 8}%)`;
      this.lightColor = `hsl(0,${sat - 10}%,${light + 10}%)`;

      this.wobble       = 0;
      this.wobbleSpeed  = 0.02 + Math.random() * 0.02;
      this.wobbleAmt    = 0.3  + Math.random() * 0.3;
      this.opacity      = 1;
      this.fadeStart    = window.innerHeight * (0.92 + Math.random() * 0.05);
      this.trailFadeT   = null;
    }

    drawTrail() {
      const ctx = this.ctx;
      const startY = this.lastY + this.size - 2;
      const endY   = this.y    + this.size * 0.5;
      const grad = ctx.createLinearGradient(this.x, startY, this.x, endY);
      grad.addColorStop(0, this.color);
      grad.addColorStop(1, this.darkColor);
      ctx.fillStyle   = grad;
      ctx.globalAlpha = 0.7 * this.opacity;
      ctx.fillRect(this.x - 0.5, startY, 1, endY - startY);
      ctx.globalAlpha = 1;
      this.lastY = this.y;
    }

    update() {
      this.speed = Math.max(0.2, this.baseSpeed + Math.sin(this.y * 0.01) * 0.1);
      this.wobble += this.wobbleSpeed;
      this.x += Math.sin(this.wobble) * this.wobbleAmt * 0.1;
      this.y += this.speed;

      this.drawTrail();

      if (this.y > this.fadeStart) {
        const p = (this.y - this.fadeStart) / (window.innerHeight - this.fadeStart);
        this.opacity = Math.max(0, 1 - p);
        this.speed  *= (1 - p * 0.5);
      }

      if (this.y <= window.innerHeight + 20) {
        const s = this.size;
        const h = s * 2 * (1 + this.speed * 0.3);
        this.ctx.save();
        this.ctx.globalAlpha = this.opacity;
        this.ctx.beginPath();
        this.ctx.moveTo(this.x, this.y);
        this.ctx.quadraticCurveTo(this.x + s*0.2, this.y + h*0.3, this.x + s*0.8, this.y + h*0.6);
        this.ctx.quadraticCurveTo(this.x + s,     this.y + h*0.8, this.x,           this.y + h);
        this.ctx.quadraticCurveTo(this.x - s,     this.y + h*0.8, this.x - s*0.8,  this.y + h*0.6);
        this.ctx.quadraticCurveTo(this.x - s*0.2, this.y + h*0.3, this.x,           this.y);
        this.ctx.closePath();
        const rg = this.ctx.createRadialGradient(this.x, this.y+h*0.3, s*0.2, this.x, this.y+h*0.5, s);
        rg.addColorStop(0, this.lightColor);
        rg.addColorStop(0.5, this.color);
        rg.addColorStop(1, this.darkColor);
        this.ctx.fillStyle = rg;
        this.ctx.fill();
        this.ctx.restore();
      } else if (!this.trailFadeT) {
        this.trailFadeT = Date.now();
      }

      const elapsed = this.trailFadeT ? Date.now() - this.trailFadeT : 0;
      const fadeRate = this.trailFadeT ? 0.15 * Math.min(elapsed / 10000, 1) : 0.003;
      this.ctx.fillStyle = `rgba(0,0,0,${fadeRate})`;
      this.ctx.globalCompositeOperation = 'destination-out';
      this.ctx.fillRect(0, 0, this.trail.width, this.trail.height);
      this.ctx.globalCompositeOperation = 'source-over';

      if (this.trailFadeT && elapsed > 10000) this.reset();
    }
  }

  function init() {
    for (let i = 0; i < maxDrops; i++) {
      setTimeout(() => {
        const d = new BloodDrop();
        d.y = -30 - Math.random() * 200;
        drops.push(d);
      }, i * 800);
    }
    (function animate() {
      drops.forEach(d => d.update());
      requestAnimationFrame(animate);
    })();
  }

  window.addEventListener('resize', () => {
    drops.forEach(d => {
      d.trail.width  = window.innerWidth;
      d.trail.height = window.innerHeight;
      if (d.x > window.innerWidth) d.reset();
    });
  });

  document.readyState === 'loading'
    ? document.addEventListener('DOMContentLoaded', init)
    : init();
})();
