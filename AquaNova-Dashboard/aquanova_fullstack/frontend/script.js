let mapInstance = null;
let marker = null;

/* =========================
   FIREBASE CONFIG
========================= */

const firebaseConfig = {
  apiKey: "AIzaSyAPDVTQg2QdszsuI_OHKf0eONtVE7KzrCw",
  authDomain: "aquanova-auth.firebaseapp.com",
  projectId: "aquanova-auth",
  storageBucket: "aquanova-auth.firebasestorage.app",
  messagingSenderId: "758613244238",
  appId: "1:758613244238:web:550efcc2e86535dfdf061f",
  measurementId: "G-WNXTQNL3P8",
};

/* =========================
   FIREBASE INITIALIZE
========================= */

firebase.initializeApp(firebaseConfig);

const auth = firebase.auth();

const provider = new firebase.auth.GoogleAuthProvider();

/* =========================
   BACKEND URL
========================= */

const API_URL = "https://aquanova-dashboard.onrender.com";

/* =========================
   THRESHOLD VALUE
========================= */

const THRESHOLD = 1;

/* =========================
   KEEP USER LOGGED IN
========================= */

auth.onAuthStateChanged(async (user) => {
  if (user) {
    try {
      document.getElementById("loginSection").style.display = "none";

      document.getElementById("dashboard").style.display = "block";

      const response = await fetch(`${API_URL}/api/auth/google-login`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          name: user.displayName,
          email: user.email,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        showAlert(data.message || "Login failed");

        await auth.signOut();

        return;
      }

      /* =========================
         RESTORE USER DETAILS
      ========================= */

      document.getElementById("userName").innerText =
        user.displayName || "User";

      document.getElementById("role").innerText = "Role: " + data.role;

      /* =========================
         ADMIN PANEL
      ========================= */

      if (data.role && data.role.toLowerCase() === "admin") {
        document.getElementById("adminPanel").style.display = "block";

        document.getElementById("adminActions").style.display = "block";
      } else {
        document.getElementById("adminPanel").style.display = "none";

        document.getElementById("adminActions").style.display = "none";
      }
      renderBoats();
      loadSensorData();
    } catch (err) {
      console.error(err);

      showAlert("Unable to connect to server");
    }
  } else {
    document.getElementById("loginSection").style.display = "flex";

    document.getElementById("dashboard").style.display = "none";
  }
});
/* =========================
   GOOGLE LOGIN
========================= */

document.getElementById("googleLogin").addEventListener("click", async () => {
  try {
    const result = await auth.signInWithPopup(provider);

    const user = result.user;

    const response = await fetch(`${API_URL}/api/auth/google-login`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        name: user.displayName,
        email: user.email,
      }),
    });

    if (!response.ok) {
      const err = await response.json();

      showAlert(err.message);

      await auth.signOut();

      return;
    }

    const data = await response.json();
    console.log(data);

    showDashboard(user.displayName, data.role);

    showSuccess("Logged in Successfully");
  } catch (err) {
    console.error(err);

    showAlert(err.message);
  }
});

/* =========================
   SHOW DASHBOARD
========================= */

function showDashboard(name, role) {
  document.getElementById("loginSection").style.display = "none";

  document.getElementById("dashboard").style.display = "block";

  document.getElementById("userName").innerText = name;

  document.getElementById("role").innerText = "Role: " + role;

  if (role === "admin") {
    document.getElementById("adminPanel").style.display = "block";

    document.getElementById("adminActions").style.display = "block";
  } else {
    document.getElementById("adminPanel").style.display = "none";

    document.getElementById("adminActions").style.display = "none";
  }

  renderBoats();
}

/* =========================
   LOGOUT
========================= */

document.getElementById("logoutBtn").addEventListener("click", async () => {
  await auth.signOut();

  location.reload();
});

/* =========================
   SENSOR DATA
========================= */

let chartInstance = null;
let customBoats = JSON.parse(localStorage.getItem("customBoats")) || [];

async function loadSensorData() {
  try {
    const response = await fetch(`${API_URL}/api/sensor-data`);
    const data = await response.json();
    /* =========================
   LAST 20 READINGS ONLY
========================= */

    const recentData = data.slice(0, 20);

    if (recentData.length === 0) return;

    const latest = recentData[0];
    document.getElementById("timeText").innerText = latest["Date and Time"];
    /* =========================
       BIN WEIGHT VALIDATION
    ========================= */

    if (
      latest.binWeight === null ||
      latest.binWeight === undefined ||
      isNaN(latest.binWeight) ||
      latest.binWeight < 0
    ) {
      showAlert("Invalid Sensor Data Detected");

      document.getElementById("binWeight").innerText = "Invalid Data";

      return;
    }

    /* =========================
       BIN WEIGHT DISPLAY
    ========================= */

    document.getElementById("binWeight").innerText = latest.binWeight + " g";

    /* =========================
   THRESHOLD ALERT
========================= */

    if (latest.binWeight > THRESHOLD) {
      document.getElementById("thresholdAlert").style.display = "block";
    } else {
      document.getElementById("thresholdAlert").style.display = "none";
    }
    const currentAlert = document.getElementById("deviceAlertIcon");

    if (currentAlert) {
      if (latest.binWeight > THRESHOLD) {
        currentAlert.style.display = "inline";
      } else {
        currentAlert.style.display = "none";
      }
    }

    /* =========================
       GPS TEXT
    ========================= */

    if (latest.location.lat === 0 && latest.location.lng === 0) {
      document.getElementById("gpsText").innerText =
        "GPS Signal Not Received. Please keep AquaNova under open sky.";
    } else {
      document.getElementById("gpsText").innerText =
        "Latitude: " +
        latest.location.lat +
        " , Longitude: " +
        latest.location.lng;
    }

    /* =========================
       CHART
    ========================= */

    const validData = recentData.filter(
      (item) =>
        item.binWeight !== null &&
        item.binWeight !== undefined &&
        !isNaN(item.binWeight) &&
        item.binWeight >= 0,
    );

    const weights = validData
      .slice()
      .reverse()
      .map((item) => item.binWeight);

    const labels = validData
      .slice()
      .reverse()
      .map((item) => item["Date and Time"].split(", ")[1]);

    const ctx = document.getElementById("weightChart");

    if (chartInstance) {
      chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
      type: "line",

      data: {
        labels,

        datasets: [
          {
            label: "Bin Weight (g)",

            data: weights,

            segment: {
              borderColor: (ctx) => {
                const value = ctx.p1.parsed.y;

                return value > THRESHOLD ? "red" : "#55ffd9";
              },
            },

            borderColor: "#55ffd9",

            backgroundColor: "rgba(85,255,217,0.15)",

            tension: 0.4,

            fill: true,

            borderWidth: 3,

            pointBackgroundColor: weights.map((weight) =>
              weight > THRESHOLD ? "red" : "#55ffd9",
            ),

            pointRadius: 5,
          },
        ],
      },

      options: {
        responsive: true,

        plugins: {
          legend: {
            labels: {
              color: "white",
            },
          },
        },

        scales: {
          x: {
            title: {
              display: true,
              text: "Time",
              color: "#55ffd9",
              font: {
                size: 16,
                weight: "bold",
              },
            },

            ticks: {
              color: "white",
            },

            grid: {
              color: "rgba(255,255,255,0.1)",
            },
          },

          y: {
            title: {
              display: true,
              text: "Bin Weight (g)",
              color: "#55ffd9",
              font: {
                size: 16,
                weight: "bold",
              },
            },

            beginAtZero: true,

            ticks: {
              color: "white",
            },

            grid: {
              color: "rgba(255,255,255,0.1)",
            },
          },
        },
      },
    });

    /* =========================
   MAP
========================= */
    const lat = Number(latest.location?.lat || 0);
    const lng = Number(latest.location?.lng || 0);

    if (lat === 0 || lng === 0) {
      document.getElementById("map").innerHTML =
        "<div style='color:white;text-align:center;padding-top:150px;font-size:18px;'>GPS Signal Not Received.<br>Keep AquaNova under open sky.</div>";
    } else {
      if (!mapInstance) {
        document.getElementById("map").innerHTML = "";

        mapInstance = L.map("map").setView([lat, lng], 18);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "OpenStreetMap",

          maxZoom: 25,
        }).addTo(mapInstance);

        marker = L.marker([lat, lng]).addTo(mapInstance);
      } else {
        marker.setLatLng([lat, lng]);

        mapInstance.panTo([lat, lng], {
          animate: true,

          duration: 1,
        });
      }
    }
  } catch (err) {
    console.error(err);

    showAlert("Unable to load sensor data");
  }
}

/* =========================
   NORMAL ALERT
========================= */

function showAlert(message) {
  const alertBox = document.getElementById("customAlert");

  alertBox.style.display = "flex";

  document.getElementById("alertText").innerText = message;
}

/* =========================
   CLOSE ALERT
========================= */

function closeAlert() {
  document.getElementById("customAlert").style.display = "none";
}

/* =========================
   SUCCESS NOTIFICATION
========================= */

function showSuccess(message) {
  const notification = document.getElementById("successNotification");

  notification.innerText = message;

  notification.style.display = "block";

  setTimeout(() => {
    notification.style.display = "none";
  }, 3000);
}
/* =========================
   AUTO REFRESH SENSOR DATA
========================= */

setInterval(() => {
  if (document.getElementById("dashboard").style.display === "block") {
    loadSensorData();
  }
}, 5000);

function renderBoats() {
  const container = document.getElementById("boatsContainer");

  container.innerHTML = `

    <button class="boatBtn selectedBoat">

      <div class="boatTop">

        <span>AquaNova 1</span>

        <span
          id="deviceAlertIcon"
          class="boatAlert"
        >
          ⚠️
        </span>

      </div>

      <div class="boatStatus">
        ● Active
      </div>

    </button>

  `;

  customBoats.forEach((boatName) => {
    container.innerHTML += `

    <button class="boatBtn">

      <div class="boatTop">

        <span>${boatName}</span>

      </div>

      <div
        class="boatStatus"
        style="color:red;"
      >
        ● Offline
      </div>

    </button>

  `;
  });
}

function toggleBoatMenu() {
  const menu = document.getElementById("boatMenu");

  if (menu.style.display === "none") {
    menu.style.display = "block";
  } else {
    menu.style.display = "none";
  }
}

function toggleUserMenu() {
  const menu = document.getElementById("userMenu");

  if (menu.style.display === "none") {
    menu.style.display = "block";
  } else {
    menu.style.display = "none";
  }
}

/* =========================
   ADD BOAT
========================= */

function addBoat() {
  const boatName = prompt("Enter Boat Name");

  if (!boatName) return;

  customBoats.push(boatName);

  localStorage.setItem("customBoats", JSON.stringify(customBoats));

  renderBoats();
}

/* =========================
   REMOVE BOAT
========================= */

function removeBoat() {
  const boatName = prompt("Enter Boat Name");

  if (!boatName) return;

  customBoats = customBoats.filter(
    (boat) => boat.toLowerCase() !== boatName.toLowerCase(),
  );

  localStorage.setItem("customBoats", JSON.stringify(customBoats));

  renderBoats();
}

/* =========================
   ADD USER
========================= */

async function addUser() {
  const email = prompt("Enter User Email");

  if (!email) return;

  await fetch(`${API_URL}/api/users`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      name: "User",
      email,
    }),
  });

  alert("User Added Successfully");
}
/* =========================
   REMOVE USER
========================= */

async function removeUser() {
  const email = prompt("Enter User Email");

  if (!email) return;

  const response = await fetch(
    `${API_URL}/api/users/email/${encodeURIComponent(email)}`,
    {
      method: "DELETE",
    },
  );

  const data = await response.json();

  alert(data.message);
}
