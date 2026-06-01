const API = "";

async function api(path, opts = {}) {
  const r = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!r.ok) {
    const err = await r.json().catch(() => ({ detail: r.statusText }));
    throw new Error(err.detail || r.statusText);
  }
  return r.json();
}

function el(id) {
  return document.getElementById(id);
}

function linesToText(arr) {
  return (arr || []).join("\n");
}

function textToLines(s) {
  return s
    .split("\n")
    .map((x) => x.trim())
    .filter(Boolean);
}

function renderTaskCard(t, showActions = false) {
  const div = document.createElement("div");
  div.className = `task-card ${t.status}`;
  div.innerHTML = `
    <span class="status">${t.status}</span>
    <div class="role">${t.role_label}</div>
    <strong>${escapeHtml(t.title)}</strong>
    <p>${escapeHtml(t.description || "").slice(0, 160)}</p>
  `;
  if (showActions && (t.status === "pending" || t.status === "in_progress")) {
    const actions = document.createElement("div");
    actions.className = "task-actions";
    const run = document.createElement("button");
    run.textContent = "Запустить";
    run.onclick = () => runTask(t.id);
    const cancel = document.createElement("button");
    cancel.className = "danger";
    cancel.textContent = "Отменить";
    cancel.onclick = () => cancelTask(t.id);
    actions.append(run, cancel);
    div.appendChild(actions);
  }
  return div;
}

function escapeHtml(s) {
  const d = document.createElement("div");
  d.textContent = s;
  return d.innerHTML;
}

function fillColumn(id, tasks, actions) {
  const node = el(id);
  node.innerHTML = "";
  if (!tasks.length) {
    node.innerHTML = '<p style="color:var(--muted);font-size:0.8rem">—</p>';
    return;
  }
  tasks.forEach((t) => node.appendChild(renderTaskCard(t, actions)));
}

async function refresh() {
  try {
    const status = await api("/api/status");
    const tasks = await api("/api/tasks");
    const events = await api("/api/events?limit=60");

    el("company-name").textContent = status.company.name;
    const badge = el("status-badge");
    badge.textContent = status.runtime.status === "running" ? "Работает" : "Ожидание";
    badge.className = "badge " + status.runtime.status;

    el("runtime-msg").textContent =
      status.runtime.message +
      (status.runtime.wave
        ? ` · волна ${status.runtime.wave}/${status.runtime.waves_total || "?"}`
        : "") +
      (status.runtime.last_error ? ` · ⚠ ${status.runtime.last_error}` : "");

    const c = status.task_counts || {};
    el("stat-pending").textContent = c.pending || 0;
    el("stat-progress").textContent = c.in_progress || 0;
    el("stat-done").textContent = c.done || 0;
    el("stat-blocked").textContent = c.blocked || 0;

    const staff = el("staff-list");
    staff.innerHTML = "";
    (status.staff || []).forEach((s) => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.textContent = s.label;
      staff.appendChild(chip);
    });

    const g = tasks.grouped;
    fillColumn("col-progress", g.in_progress, false);
    fillColumn("col-pending", g.pending, true);
    fillColumn("col-done", g.done, false);
    fillColumn("col-blocked", g.blocked, false);

    const ev = el("events");
    ev.innerHTML = "";
    events.events
      .slice()
      .reverse()
      .forEach((e) => {
        const div = document.createElement("div");
        div.className = "event";
        let detail = "";
        if (e.title) detail += ` ${e.title}`;
        if (e.role) detail += ` [${e.role}]`;
        if (e.error) detail += ` — ${e.error}`;
        div.innerHTML = `<div class="ts">${e.ts || ""}</div><span class="type">${e.type}</span>${escapeHtml(detail)}`;
        ev.appendChild(div);
      });

    document.querySelectorAll("button[data-needs-running]").forEach((b) => {
      b.disabled = status.running;
    });
  } catch (err) {
    console.error(err);
  }
}

async function loadDirectives() {
  const d = await api("/api/directives");
  el("directives-do").value = linesToText(d.do);
  el("directives-dont").value = linesToText(d.dont);
  el("directives-free").value = d.freeform || "";
}

async function saveDirectives() {
  await api("/api/directives", {
    method: "POST",
    body: JSON.stringify({
      do: el("directives-do").value,
      dont: el("directives-dont").value,
      freeform: el("directives-free").value,
    }),
  });
  alert("Указания сохранены — агенты увидят их в следующих задачах");
}

async function startCycle(mock, forceNew) {
  await api("/api/cycle/start", {
    method: "POST",
    body: JSON.stringify({ mock, force_new: forceNew }),
  });
  refresh();
}

async function addTask() {
  const role = el("new-task-role").value;
  const description = el("new-task-desc").value.trim();
  if (!description) {
    alert("Опишите задачу");
    return;
  }
  const body = {
    role,
    description,
    title: el("new-task-title").value.trim() || "Задача от владельца",
  };
  const t = await api("/api/tasks", { method: "POST", body: JSON.stringify(body) });
  el("new-task-desc").value = "";
  const run = confirm("Задача создана. Запустить сейчас?");
  if (run) await runTask(t.id);
  refresh();
}

async function runTask(id) {
  await api(`/api/tasks/${id}/run?mock=true`, { method: "POST" });
  refresh();
}

async function cancelTask(id) {
  if (!confirm("Отменить задачу?")) return;
  await api(`/api/tasks/${id}/cancel`, { method: "POST" });
  refresh();
}

async function loadRoles() {
  const status = await api("/api/status");
  const sel = el("new-task-role");
  sel.innerHTML = "";
  status.roles_available.forEach((r) => {
    const o = document.createElement("option");
    o.value = r.id;
    o.textContent = r.label + (r.hired ? "" : " (найм при запуске)");
    sel.appendChild(o);
  });
}

function bind() {
  el("btn-cycle-mock").onclick = () => startCycle(true, false);
  el("btn-cycle-mock-new").onclick = () => startCycle(true, true);
  el("btn-cycle-api").onclick = () => startCycle(false, false);
  el("btn-save-directives").onclick = () => saveDirectives().catch(alert);
  el("btn-add-task").onclick = () => addTask().catch(alert);
}

bind();
loadDirectives();
loadRoles();
refresh();
setInterval(refresh, 2500);
