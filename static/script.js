document.getElementById('habitForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  const name = document.getElementById('habitName').value;
  const res = await fetch('/habits', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name })
  });
  const data = await res.json();
  addHabitToUI(data);
});

window.onload = async function () {
  const res = await fetch('/habits');
  const data = await res.json();
  data.forEach(addHabitToUI);
};

function addHabitToUI(habit) {
  const li = document.createElement('li');
  li.textContent = habit.name;
  document.getElementById('habitList').appendChild(li);
}
