document.addEventListener('DOMContentLoaded', function(){
  // Simple, unobtrusive hero reveal
  const hero = document.querySelector('.hero-copy');
  if(hero){
    hero.style.opacity = 0;
    hero.style.transform = 'translateY(6px)';
    setTimeout(()=>{
      hero.style.transition = 'opacity .6s ease, transform .6s ease';
      hero.style.opacity = 1;
      hero.style.transform = 'translateY(0)';
    }, 120);
  }

  // Demo CTA: smooth scroll to features
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', (e) => {
      const href = a.getAttribute('href');
      if(href.length>1){
        const el = document.querySelector(href);
        if(el){
          e.preventDefault();
          el.scrollIntoView({behavior:'smooth',block:'start'});
        }
      }
    });
  });

  // Count-up animation for stats when visible
  const stats = document.querySelectorAll('.stats strong[data-target]');
  function animateCounts(){
    stats.forEach(el => {
      if(el.dataset.animated) return;
      const rect = el.getBoundingClientRect();
      if(rect.top < window.innerHeight && rect.bottom >= 0){
        el.dataset.animated = 'true';
        const target = parseInt(el.getAttribute('data-target'),10) || 0;
        const start = 0;
        const duration = 1200;
        let startTime = null;
        function step(ts){
          if(!startTime) startTime = ts;
          const progress = Math.min((ts - startTime) / duration, 1);
          const value = Math.floor(progress * (target - start) + start);
          // format thousands as 4.6k for readability when large
          if(target >= 1000){
            const short = (value/1000).toFixed(value>=10000?0:1).replace(/\.0$/,'') + 'k';
            el.textContent = short;
          } else {
            el.textContent = String(value);
          }
          if(progress < 1){
            requestAnimationFrame(step);
          }
        }
        requestAnimationFrame(step);
      }
    });
  }

  window.addEventListener('scroll', animateCounts, {passive:true});
  animateCounts();
});
