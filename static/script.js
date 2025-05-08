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

window.onload = async function () {
  const res = await fetch(`/habits?user_id=${userId}`); // <-- Fetch user-specific habits
  const data = await res.json();
  data.forEach(addHabitToUI);
};

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

