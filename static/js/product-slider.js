document.querySelectorAll(".slider-shell").forEach((shell) => {
  const slider = shell.querySelector(".product-slider");
  const slides = slider.querySelectorAll(".slide");
  const previous = shell.querySelector(".slider-prev");
  const next = shell.querySelector(".slider-next");
  if (!slides.length || !previous || !next) return;

  const currentIndex = () => Math.round(slider.scrollLeft / slider.clientWidth);
  const goTo = (index) => {
    const safeIndex = (index + slides.length) % slides.length;
    slider.scrollTo({ left: safeIndex * slider.clientWidth, behavior: "smooth" });
  };

  previous.addEventListener("click", () => goTo(currentIndex() - 1));
  next.addEventListener("click", () => goTo(currentIndex() + 1));
});
