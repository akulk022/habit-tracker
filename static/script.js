// Get the logged-in user ID
const userId = localStorage.getItem('user_id');

// Redirect to login if not logged in
if (!userId) {
  window.location.href = "/login";
}

document.getElementById('habitForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const name = document.getElementById('habitName').value;

  const res = await fetch('/habits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, user_id: userId }) // <-- Send user_id
  });

  const data = await res.json();
  addHabitToUI(data);
  document.getElementById('habitName').value = ''; // Clear input
});

function addHabitToUI(habit) {
  const li = document.createElement('li');

  const checkbox = document.createElement('input');
  checkbox.type = 'checkbox';
  checkbox.checked = habit.done;
  checkbox.disabled = habit.done;

  checkbox.addEventListener('change', async () => {
    await fetch(`/complete/${habit.id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId }) // <-- Send user_id on completion
    });
    checkbox.disabled = true;
  });

  const label = document.createElement('span');
  label.textContent = habit.name;

  li.appendChild(checkbox);
  li.appendChild(label);

  document.getElementById('habitList').appendChild(li);
}

document.getElementById('logoutBtn').addEventListener('click', () => {
  localStorage.removeItem('user_id');
  window.location.href = '/login';
});

const username = localStorage.getItem('username');
document.getElementById('greeting').textContent = `Welcome, ${username}!`;

// Load goals on page load
window.onload = async function () {
  // Load habits
  const res = await fetch(`/habits?user_id=${userId}`);
  const data = await res.json();
  data.forEach(addHabitToUI);

  // Load goals
  const goalRes = await fetch(`/goals?user_id=${userId}`);
  const goals = await goalRes.json();
  goals.forEach(addGoalToUI);

  // Create heatmap
  const heatmapContainer = document.getElementById('heatmapGrid');
  for (let i = 0; i < 7 * 53; i++) {  // 7 rows, 53 columns
    const level = Math.ceil(Math.random() * 5);
    const cell = document.createElement('div');
    cell.classList.add(`heat-${level}`);
    heatmapContainer.appendChild(cell);
  }
};


// Add new goal
document.getElementById('goalForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const description = document.getElementById('goalInput').value;

  const res = await fetch('/goals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, description })
  });

  const goal = await res.json();
  addGoalToUI(goal);
  document.getElementById('goalInput').value = '';
});

function addGoalToUI(goal) {
  const li = document.createElement('li');
  li.textContent = goal.description;
  document.getElementById('goalList').appendChild(li);
}

// Sample weekly chart (7 days)
const weeklyCtx = document.getElementById('weeklyChart').getContext('2d');
new Chart(weeklyCtx, {
  type: 'bar',
  data: {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [{
      label: 'Completions',
      data: [2, 3, 4, 1, 5, 3, 6],
      backgroundColor: '#32cd32'
    }]
  },
  options: {
    scales: {
      y: { beginAtZero: true }
    }
  }
});

// Sample monthly chart (30 days)
const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
new Chart(monthlyCtx, {
  type: 'line',
  data: {
    labels: Array.from({length: 30}, (_, i) => `Day ${i + 1}`),
    datasets: [{
      label: 'Completions',
      data: Array.from({length: 30}, () => Math.floor(Math.random() * 6)),
      borderColor: '#228b22',
      fill: false,
      tension: 0.3
    }]
  },
  options: {
    scales: {
      y: { beginAtZero: true }
    }
  }
});



