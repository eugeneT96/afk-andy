// MathMatrix — Main JS
// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add subtle parallax effect to floating math symbols
document.addEventListener('mousemove', (e) => {
    const symbols = document.querySelectorAll('.float-symbol');
    const mouseX = e.clientX / window.innerWidth - 0.5;
    const mouseY = e.clientY / window.innerHeight - 0.5;

    symbols.forEach((symbol, index) => {
        const speed = (index + 1) * 5;
        const x = mouseX * speed;
        const y = mouseY * speed;
        symbol.style.transform = `translate(${x}px, ${y}px)`;
    });
});
