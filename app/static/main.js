const form = document.getElementById("activity-form");
const tableBody = document.getElementById("activity-table");
const message = document.getElementById("form-message");
const stravaButton = document.getElementById("strava-login");
const stravaMessage = document.getElementById("strava-message");
const summaryNodes = {
  total: document.getElementById("summary-total"),
  minutes: document.getElementById("summary-minutes"),
  athletes: document.getElementById("summary-athletes"),
  favorite: document.getElementById("summary-favorite"),
};

if (stravaButton && stravaMessage) {
  stravaButton.addEventListener("click", async () => {
    stravaButton.disabled = true;
    stravaMessage.textContent = "Redirigiendo a Strava...";
    stravaMessage.style.color = "#111";

    try {
      const response = await fetch("/api/auth/strava/login");
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "No fue posible iniciar sesión con Strava");
      }

      const data = await response.json();
      window.location.href = data.authorize_url;
    } catch (error) {
      stravaMessage.textContent = error.message;
      stravaMessage.style.color = "#dc2626";
      stravaButton.disabled = false;
    }
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form));
  payload.duration_minutes = Number(payload.duration_minutes);

  try {
    const response = await fetch("/api/activities", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "No se pudo guardar la actividad");
    }

    form.reset();
    message.textContent = "Actividad registrada";
    message.style.color = "#059669";
    await Promise.all([loadActivities(), loadSummary()]);
  } catch (error) {
    message.textContent = error.message;
    message.style.color = "#dc2626";
  }
});

async function loadActivities() {
  const response = await fetch("/api/activities");
  const activities = await response.json();
  tableBody.innerHTML = activities
    .map(
      (activity) => `
        <tr>
          <td>${new Date(activity.activity_date).toLocaleDateString()}</td>
          <td>${activity.athlete_name}</td>
          <td>${activity.activity_type}</td>
          <td>${activity.duration_minutes} min</td>
          <td>${activity.intensity_level}</td>
          <td>${activity.notes ?? ""}</td>
        </tr>
      `,
    )
    .join("");
}

async function loadSummary() {
  const response = await fetch("/api/summary");
  const summary = await response.json();
  summaryNodes.total.textContent = summary.total_sessions;
  summaryNodes.minutes.textContent = summary.total_minutes;
  summaryNodes.athletes.textContent = summary.unique_athletes;
  summaryNodes.favorite.textContent = summary.favorite_activity ?? "-";
}

loadActivities();
loadSummary();
