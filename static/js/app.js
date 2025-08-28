// Mostrar y ocultar mensajes flash automáticamente
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(flash => {
    setTimeout(() => {
      flash.style.display = "none";
    }, 4000); // se ocultan después de 4 segundos
  });
});
