/* scripts.js */

// Navigation Tab Switching
function navTo(sectId) {
  document.querySelectorAll('.playbook-section').forEach(sect => {
    sect.classList.remove('active');
    sect.style.display = 'none'; // force hide inactive sections
  });
  document.querySelectorAll('.dock-item').forEach(link => {
    link.classList.remove('active');
  });

  const target = document.getElementById('sect-' + sectId);
  if (target) {
    target.classList.add('active');
    target.style.display = 'block'; // force show active section
  }

  const activeLink = Array.from(document.querySelectorAll('.dock-item')).find(link => 
    link.getAttribute('onclick').includes(sectId)
  );
  if (activeLink) activeLink.classList.add('active');

  const contentFrame = document.querySelector('.content-frame');
  if (contentFrame) contentFrame.scrollTo({ top: 0, behavior: 'smooth' });
}

// Expand/Collapse Accordion Items
function toggleAccordion(header) {
  const item = header.parentElement;
  item.classList.toggle('open');
}

// Copy Code Utility
function copyCode(btn) {
  const pre = btn.nextElementSibling;
  if (!pre) return;

  const lines = pre.innerText.split('\n');
  const cleanLines = lines.filter(line => !line.trim().startsWith('#') && !line.trim().startsWith('//'));
  const textToCopy = cleanLines.join('\n').trim();

  navigator.clipboard.writeText(textToCopy).then(() => {
    const originalText = btn.innerText;
    btn.innerText = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => {
      btn.innerText = originalText;
      btn.classList.remove('copied');
    }, 1500);
  });
}

// Scroll back to top inside content frame
function scrollToTop() {
  const contentFrame = document.querySelector('.content-frame');
  if (contentFrame) contentFrame.scrollTo({ top: 0, behavior: 'smooth' });
}

// Watch scroll events inside content frame to show/hide back-top scroller button
document.addEventListener('DOMContentLoaded', () => {
  const contentFrame = document.querySelector('.content-frame');
  const topScroller = document.getElementById('back-top');
  
  if (contentFrame && topScroller) {
    contentFrame.addEventListener('scroll', () => {
      if (contentFrame.scrollTop > 250) {
        topScroller.classList.add('visible');
      } else {
        topScroller.classList.remove('visible');
      }
    });
  }
});

// Strip previous highlights
function stripHighlight(el) {
  const marks = el.querySelectorAll('mark');
  marks.forEach(mark => {
    const parent = mark.parentNode;
    parent.replaceChild(document.createTextNode(mark.textContent), mark);
    parent.normalize();
  });
}

// Recursively highlight text nodes
function highlightTextNodes(node, regex) {
  if (node.nodeType === 3) { // Text node
    const matches = node.nodeValue.match(regex);
    if (matches) {
      const span = document.createElement('span');
      span.innerHTML = node.nodeValue.replace(regex, match => `<mark>${match}</mark>`);
      node.parentNode.replaceChild(span, node);
      return 1;
    }
  } else if (node.nodeType === 1 && node.childNodes && !['SCRIPT', 'STYLE', 'PRE', 'CODE', 'MARK'].includes(node.nodeName)) {
    let matchCount = 0;
    for (let i = node.childNodes.length - 1; i >= 0; i--) {
      matchCount += highlightTextNodes(node.childNodes[i], regex);
    }
    return matchCount;
  }
  return 0;
}

// Enhanced search function
function searchPlaybook() {
  const query = document.getElementById('playbook-search').value.toLowerCase().trim();
  const feedback = document.getElementById('search-feedback');
  
  const cards = document.querySelectorAll('.info-card');
  const accordions = document.querySelectorAll('.accordion-item');
  const ports = document.querySelectorAll('.port-item-box');
  const sections = document.querySelectorAll('.playbook-section');

  // Clear previous highlights
  cards.forEach(card => stripHighlight(card));
  accordions.forEach(acc => stripHighlight(acc));
  ports.forEach(p => stripHighlight(p));

  if (query === '') {
    // Restore default layout visibility
    sections.forEach(s => {
      s.style.display = 'none'; // hide all first
      s.querySelectorAll('h1, h2, .accent-line, .section-intro').forEach(el => el.style.display = '');
    });
    cards.forEach(card => card.style.display = '');
    accordions.forEach(acc => {
      acc.style.display = '';
      acc.classList.remove('open');
    });
    ports.forEach(p => p.style.display = '');
    
    // Switch to active tab view
    const activeLink = document.querySelector('.dock-item.active');
    if (activeLink) {
      const onclickAttr = activeLink.getAttribute('onclick');
      const match = onclickAttr.match(/'([^']+)'/);
      if (match) navTo(match[1]);
    }
    
    if (feedback) feedback.style.display = 'none';
    return;
  }

  // Escape special regex chars
  const escapedQuery = query.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
  const regex = new RegExp(escapedQuery, 'gi');
  let matchCount = 0;

  // Search through elements
  sections.forEach(section => {
    let sectionMatchCount = 0;

    // Search cards inside this section
    section.querySelectorAll('.info-card').forEach(card => {
      const hasMatch = highlightTextNodes(card, regex);
      if (hasMatch > 0) {
        card.style.display = '';
        sectionMatchCount++;
        matchCount++;
      } else {
        card.style.display = 'none';
      }
    });

    // Search accordions inside this section
    section.querySelectorAll('.accordion-item').forEach(acc => {
      const hasMatch = highlightTextNodes(acc, regex);
      if (hasMatch > 0) {
        acc.style.display = '';
        acc.classList.add('open'); // open accordion containing matching terms
        sectionMatchCount++;
        matchCount++;
      } else {
        acc.style.display = 'none';
      }
    });

    // Search ports inside this section
    section.querySelectorAll('.port-item-box').forEach(p => {
      const hasMatch = highlightTextNodes(p, regex);
      if (hasMatch > 0) {
        p.style.display = '';
        sectionMatchCount++;
        matchCount++;
      } else {
        p.style.display = 'none';
      }
    });

    // Hide/Show section & its header nodes based on child match presence
    if (sectionMatchCount > 0) {
      section.style.display = 'block';
      section.querySelectorAll('h1, h2, .accent-line, .section-intro').forEach(el => el.style.display = '');
    } else {
      section.style.display = 'none';
    }
  });

  // Update search UI feedback
  if (feedback) {
    feedback.style.display = 'block';
    feedback.innerHTML = `Found <strong>${matchCount}</strong> match(es) across all guides for: "<em>${query}</em>"`;
  }
}

// HTML5 Canvas Background: Floating Color Orbs + Constellation Network
const canvas = document.getElementById('orb-canvas');
if (canvas) {
  const ctx = canvas.getContext('2d');
  let mouse = { x: undefined, y: undefined };

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  window.addEventListener('mouseout', () => {
    mouse.x = undefined;
    mouse.y = undefined;
  });

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // Dim Color Orbs for background depth
  class Orb {
    constructor(color, size) {
      this.size = size;
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.color = color;
      this.vx = (Math.random() - 0.5) * 0.3;
      this.vy = (Math.random() - 0.5) * 0.3;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < -this.size) this.x = canvas.width + this.size;
      if (this.x > canvas.width + this.size) this.x = -this.size;
      if (this.y < -this.size) this.y = canvas.height + this.size;
      if (this.y > canvas.height + this.size) this.y = -this.size;

      // Mouse push
      if (mouse.x !== undefined && mouse.y !== undefined) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 300) {
          const force = (300 - distance) / 300;
          this.x -= (dx / distance) * force * 1.5;
          this.y -= (dy / distance) * force * 1.5;
        }
      }
    }

    draw() {
      const gradient = ctx.createRadialGradient(
        this.x, this.y, 0,
        this.x, this.y, this.size
      );
      gradient.addColorStop(0, this.color);
      gradient.addColorStop(1, 'rgba(2, 3, 6, 0)');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // Constellation Particles in foreground
  class Particle {
    constructor() {
      this.x = Math.random() * canvas.width;
      this.y = Math.random() * canvas.height;
      this.size = Math.random() * 2 + 1.2;
      this.vx = (Math.random() - 0.5) * 0.45;
      this.vy = (Math.random() - 0.5) * 0.45;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0) this.x = canvas.width;
      if (this.x > canvas.width) this.x = 0;
      if (this.y < 0) this.y = canvas.height;
      if (this.y > canvas.height) this.y = 0;

      // Mouse push
      if (mouse.x !== undefined && mouse.y !== undefined) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance < 120) {
          const force = (120 - distance) / 120;
          this.x -= (dx / distance) * force * 1.2;
          this.y -= (dy / distance) * force * 1.2;
        }
      }
    }

    draw() {
      ctx.fillStyle = 'rgba(239, 68, 110, 0.7)'; // Crimson red nodes
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const orbs = [
    new Orb('rgba(239, 68, 110, 0.045)', 350),  // Crimson Pink
    new Orb('rgba(0, 82, 255, 0.04)', 400),    // Electric Blue
    new Orb('rgba(126, 34, 206, 0.045)', 350)   // Deep Purple
  ];

  const particles = [];
  const particleCount = 80;
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function drawLines() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 110) {
          const alpha = (110 - dist) / 110 * 0.15;
          ctx.strokeStyle = `rgba(239, 68, 110, ${alpha})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background dim glowing orbs first
    orbs.forEach(orb => {
      orb.update();
      orb.draw();
    });

    // Draw foreground constellation particles
    particles.forEach(p => {
      p.update();
      p.draw();
    });
    drawLines();
    
    requestAnimationFrame(animate);
  }
  animate();
}
