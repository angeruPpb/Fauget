console.log("JavaScript cargado correctamente!");
document.addEventListener("DOMContentLoaded", () => {
  const links = document.querySelectorAll(".sidebar a");
  const mainContent = document.getElementById("main-content");

  if (!mainContent) return;

  links.forEach(link => {
    link.addEventListener("click", async (e) => {
      e.preventDefault();
      const url = link.getAttribute("href");

      try {
        const response = await fetch(url);
        if (!response.ok) throw new Error("Página no encontrada");

        const html = await response.text();
        mainContent.innerHTML = html;

        // Puedes agregar lógica aquí para resaltar el botón activo, etc.
      } catch (err) {
        mainContent.innerHTML = `<p style="color:red;">Error al cargar la página: ${err.message}</p>`;
      }
    });
  });
});
