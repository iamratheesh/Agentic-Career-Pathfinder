import React, { useEffect, useRef } from 'react';
import styles from './Loader.module.css';

const Loader = () => {
  const canvasRef = useRef(null);
  const loaderTextRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const loaderText = loaderTextRef.current;

    const size = 300;
    const dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    ctx.scale(dpr, dpr);
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    const center = { x: size / 2, y: size / 2 };

    const g1 = ctx.createLinearGradient(0, 0, size, size);
    g1.addColorStop(0.1886, '#348CFF');
    g1.addColorStop(0.8114, '#1EECB2');

    const g2 = ctx.createLinearGradient(0, size, size, 0);
    g2.addColorStop(0, '#2F63C5');
    g2.addColorStop(0.5428, '#2882FA');

    const g3 = ctx.createLinearGradient(0, 0, size, 0);
    g3.addColorStop(0, '#2F63C5');
    g3.addColorStop(0.8168, '#2882FA');

    const g4 = ctx.createLinearGradient(0, 0, size, size);
    g4.addColorStop(0.1886, '#28A2B1');
    g4.addColorStop(0.8114, '#1EECB2');

    const svgPathString = "M55.632 62.732C58.0967 61.6602 60.0232 59.6371 60.9733 57.123L80.0526 6.63797C83.2951 -1.94181 95.4319 -1.94183 98.6744 6.63796L117.754 57.123C118.704 59.6371 120.63 61.6602 123.095 62.732L171.946 83.9769C179.925 87.4467 179.925 98.7626 171.946 102.232L123.095 123.477C120.63 124.549 118.704 126.572 117.754 129.086L98.6744 179.571C95.4319 188.151 83.2951 188.151 80.0526 179.571L60.9733 129.086C60.0232 126.572 58.0967 124.549 55.632 123.477L6.78091 102.232C-1.1978 98.7626 -1.19781 87.4467 6.7809 83.9769L55.632 62.732Z";
    const starPath = new Path2D(svgPathString);

    const drawStarFromPath = (cx, cy, scale, color, rotation = 0, opacity = 1) => {
      ctx.save();
      ctx.globalAlpha = opacity;
      ctx.translate(cx, cy);
      ctx.rotate(rotation);
      ctx.scale(scale, scale);
      ctx.translate(-89.36, -93.1);
      ctx.shadowColor = 'rgba(0, 0, 0, 0.1)';
      ctx.shadowBlur = 10 * scale;
      ctx.fillStyle = color;
      ctx.fill(starPath);
      ctx.restore();
    };

    let frame = 0;
    let majorStars = [];
    let satelliteStars = [];
    let cometParticles = [];

    class CometParticle {
      constructor(parentStar) {
        this.x = parentStar.x;
        this.y = parentStar.y;
        const angle = parentStar.movementAngle + Math.PI;
        const spread = Math.PI / 2;
        const finalAngle = angle + (Math.random() - 0.5) * spread;
        const speed = Math.random() * 1.5 + 0.5;
        this.vx = Math.cos(finalAngle) * speed;
        this.vy = Math.sin(finalAngle) * speed;
        this.scale = parentStar.currentScale * (Math.random() * 0.2 + 0.1);
        this.life = 70;
        this.maxLife = 70;
        this.color = parentStar.color;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vx *= 0.98;
        this.vy *= 0.98;
        this.life--;

        const progress = this.life / this.maxLife;
        const scale = this.scale * progress;
        drawStarFromPath(this.x, this.y, scale, this.color);
      }
    }

    class Star {
      constructor(config) {
        Object.assign(this, config);
        this.x = this.originX;
        this.y = this.originY;
        this.pulseOffset = Math.random() * Math.PI * 2;
        this.movementAngle = 0;
        if (this.type === 'satellite') {
          this.orbitSpeed = 0.015 + Math.random() * 0.005;
        } else {
          this.hoverRadius = 5;
          this.hoverSpeed = 0.005 + Math.random() * 0.005;
        }
      }

      update(frame, orbitCenter) {
        const oldX = this.x;
        const oldY = this.y;

        if (this.type === 'satellite') {
          const progress = Math.sin(frame * this.orbitSpeed + this.pulseOffset);
          const pathX = this.pathRadius * progress * this.pathDirection;
          const pathY = this.pathRadius * progress;
          this.x = orbitCenter.x + pathX;
          this.y = orbitCenter.y + pathY;
          if (frame % 5 === 0) {
            this.movementAngle = Math.atan2(this.y - oldY, this.x - oldX);
            cometParticles.push(new CometParticle(this));
          }
        } else {
          this.x = this.originX + Math.cos(frame * this.hoverSpeed + this.pulseOffset) * this.hoverRadius;
          this.y = this.originY + Math.sin(frame * this.hoverSpeed + this.pulseOffset) * this.hoverRadius;
        }

        const perspective = this.type === 'satellite' ? Math.sin(frame * this.orbitSpeed + this.pulseOffset) : 1;
        const scale3D = this.type === 'satellite' ? (Math.abs(perspective) * 0.5 + 0.5) : 1;
        const pulse = Math.sin(frame * 0.02 + this.pulseOffset) * 0.02;
        this.currentScale = (this.baseScale + pulse) * scale3D;
        const opacity = scale3D * 0.7 + 0.3;
        drawStarFromPath(this.x, this.y, this.currentScale, this.color, 0, opacity);
      }
    }

    const init = () => {
      majorStars = [];
      satelliteStars = [];
      cometParticles = [];

      const starLayout = [
        { type: 'major', originX: center.x - 30, originY: center.y + 15, baseScale: 0.22, color: g1 },
        { type: 'major', originX: center.x + 15, originY: center.y - 10, baseScale: 0.28, color: g2 },
        { type: 'satellite', pathRadius: 60, pathDirection: 1, baseScale: 0.12, color: g4 },
        { type: 'satellite', pathRadius: 75, pathDirection: -1, baseScale: 0.1, color: g3 },
      ];

      starLayout.forEach(config => {
        const star = new Star(config);
        config.type === 'major' ? majorStars.push(star) : satelliteStars.push(star);
      });
    };

    const animate = () => {
      frame++;
      ctx.clearRect(0, 0, size, size);

      cometParticles.forEach((p, index) => {
        p.update();
        if (p.life <= 0) cometParticles.splice(index, 1);
      });

      const orbitCenterX = (majorStars[0].x + majorStars[1].x) / 2;
      const orbitCenterY = (majorStars[0].y + majorStars[1].y) / 2;
      const allStars = [...majorStars, ...satelliteStars].sort((a, b) => a.y - b.y);
      allStars.forEach(star => star.update(frame, { x: orbitCenterX, y: orbitCenterY }));

      requestAnimationFrame(animate);
    };

    let charIndex = 0;
    let isDeleting = false;
    const typingText = "THINKING...";

    const typeEffect = () => {
      const currentText = typingText.substring(0, charIndex);
      loaderText.textContent = currentText;

      if (!isDeleting) {
        charIndex++;
        if (charIndex > typingText.length) {
          isDeleting = true;
          setTimeout(typeEffect, 2000);
        } else {
          setTimeout(typeEffect, 150);
        }
      } else {
        charIndex--;
        if (charIndex < 0) {
          isDeleting = false;
          charIndex = 0;
          setTimeout(typeEffect, 500);
        } else {
          setTimeout(typeEffect, 100);
        }
      }
    };

    init();
    animate();
    typeEffect();
  }, []);

  return (
    <div className={styles.loaderWrapper}>
      <canvas ref={canvasRef} className={styles.canvas} />
      <p ref={loaderTextRef} className={styles.text}></p>
    </div>
  );
};

export default Loader;
