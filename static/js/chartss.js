// Renderizar un gráfico en el dashboard si existe el canvas
document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("eventsChart");
  if (ctx) {
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Reconocidos", "Desconocidos"],
        datasets: [{
          label: "Eventos detectados",
          data: [12, 5], // Estos datos los puedes pasar dinámicamente desde Flask
          backgroundColor: ["#28a745", "#dc3545"]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "top" },
          title: { display: true, text: "Resumen de eventos" }
        }
      }
    });
  }
});
