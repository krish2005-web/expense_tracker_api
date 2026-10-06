const API_BASE = "http://127.0.0.1:8000";

let token = localStorage.getItem("access_token");
let page = 1;
const limit = 10;
let isRegisterMode = false;

const $ = (id) => document.getElementById(id);

const authSection = $("authSection");
const appSection = $("appSection");
const authForm = $("authForm");
const authMessage = $("authMessage");
const expenseMessage = $("expenseMessage");

function setMessage(el, text = "", ok = false) {
  el.textContent = text;
  el.style.color = ok ? "#15803d" : "#b91c1c";
}

async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  let data = null;
  const text = await response.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!response.ok) {
    throw new Error(
      typeof data === "object" && data?.detail
        ? Array.isArray(data.detail)
          ? data.detail.map((e) => e.msg).join(", ")
          : data.detail
        : `Request failed: ${response.status}`
    );
  }

  return data;
}

function showLoginMode() {
  isRegisterMode = false;
  $("loginTab").classList.add("active");
  $("registerTab").classList.remove("active");
  $("nameGroup").classList.add("hidden");
  $("name").required = false;
  $("authSubmit").textContent = "Login";
  setMessage(authMessage, "");
}

function showRegisterMode() {
  isRegisterMode = true;
  $("registerTab").classList.add("active");
  $("loginTab").classList.remove("active");
  $("nameGroup").classList.remove("hidden");
  $("name").required = true;
  $("authSubmit").textContent = "Register";
  setMessage(authMessage, "");
}

async function handleAuth(event) {
  event.preventDefault();

  const email = $("email").value.trim();
  const password = $("password").value;

  try {
    if (isRegisterMode) {
      const name = $("name").value.trim();

      await apiFetch("/auth/register", {
        method: "POST",
        body: JSON.stringify({ name, email, password })
      });

      setMessage(authMessage, "Registration successful. You can now login.", true);
      authForm.reset();
      showLoginMode();
      return;
    }

    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });

    token = data.access_token;
    localStorage.setItem("access_token", token);

    authForm.reset();
    await loadApp();
  } catch (error) {
    setMessage(authMessage, error.message);
  }
}

async function loadApp() {
  try {
    const me = await apiFetch("/me");
    authSection.classList.add("hidden");
    appSection.classList.remove("hidden");
    $("logoutBtn").classList.remove("hidden");
    $("userInfo").textContent = `${me.name} • ${me.email}`;
    await Promise.all([loadExpenses(), loadSummary(), loadCategorySummary()]);
  } catch (error) {
    logout();
    setMessage(authMessage, error.message);
  }
}

function logout() {
  token = null;
  localStorage.removeItem("access_token");
  appSection.classList.add("hidden");
  authSection.classList.remove("hidden");
  $("logoutBtn").classList.add("hidden");
  showLoginMode();
}

async function loadExpenses() {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit)
  });

  const category = $("filterCategory").value;
  const minAmount = $("minAmount").value;
  const maxAmount = $("maxAmount").value;

  if (category) params.set("category", category);
  if (minAmount) params.set("min_amount", minAmount);
  if (maxAmount) params.set("max_amount", maxAmount);

  try {
    const expenses = await apiFetch(`/expense/?${params.toString()}`);
    const list = $("expenseList");
    list.innerHTML = "";

    if (!expenses.length) {
      list.innerHTML = "<p class='muted'>No expenses found.</p>";
    } else {
      expenses.forEach((expense) => {
        const item = document.createElement("div");
        item.className = "expense-item";
        item.innerHTML = `
          <div class="expense-main">
            <h3>${escapeHtml(expense.title)}</h3>
            <div class="expense-meta">
              ${escapeHtml(expense.category)} • ${escapeHtml(expense.expense_date)}
            </div>
            <div class="expense-meta">${escapeHtml(expense.description || "")}</div>
          </div>
          <div class="expense-actions">
            <div class="expense-amount">₹${Number(expense.amount).toFixed(2)}</div>
            <button type="button" class="edit-btn" data-id="${expense.id}">Edit</button>
            <button type="button" class="delete-btn" data-id="${expense.id}">Delete</button>
          </div>
        `;
        list.appendChild(item);
      });
    }

    $("pageInfo").textContent = `Page ${page}`;
    $("prevBtn").disabled = page === 1;
    $("nextBtn").disabled = expenses.length < limit;
  } catch (error) {
    setMessage($("globalMessage"), error.message);
  }
}

async function loadSummary() {
  try {
    const data = await apiFetch("/expense/summary");
    $("totalExpense").textContent = `₹${Number(data.total_expense || 0).toFixed(2)}`;
    $("totalCount").textContent = data.total_count || 0;
    $("averageExpense").textContent = `₹${Number(data.average_expense || 0).toFixed(2)}`;
  } catch (error) {
    setMessage($("globalMessage"), error.message);
  }
}

async function loadCategorySummary() {
  try {
    const data = await apiFetch("/expense/summary/categories");
    const box = $("categorySummary");
    box.innerHTML = "<h3>Category Summary</h3>";

    const entries = Object.entries(data || {});
    if (!entries.length) {
      box.innerHTML += "<p class='muted'>No category data.</p>";
      return;
    }

    entries.forEach(([category, values]) => {
      const row = document.createElement("div");
      row.className = "summary-row";

      if (typeof values === "object" && values !== null) {
        row.innerHTML = `
          <span>${escapeHtml(category)} (${values.count ?? 0})</span>
          <strong>₹${Number(values.total || 0).toFixed(2)}</strong>
        `;
      } else {
        row.innerHTML = `
          <span>${escapeHtml(category)}</span>
          <strong>₹${Number(values || 0).toFixed(2)}</strong>
        `;
      }

      box.appendChild(row);
    });
  } catch (error) {
    setMessage($("globalMessage"), error.message);
  }
}

async function addExpense(event) {
  event.preventDefault();

  try {
    const payload = {
      title: $("title").value.trim(),
      amount: Number($("amount").value),
      category: $("category").value,
      description: $("description").value.trim() || null,
      expense_date: $("expenseDate").value
    };

    await apiFetch("/expense/", {
      method: "POST",
      body: JSON.stringify(payload)
    });

    setMessage(expenseMessage, "Expense added successfully.", true);
    $("expenseForm").reset();
    await Promise.all([loadExpenses(), loadSummary(), loadCategorySummary()]);
  } catch (error) {
    setMessage(expenseMessage, error.message);
  }
}


async function deleteExpense(expenseId) {
  const confirmed = window.confirm("Delete this expense?");
  if (!confirmed) return;

  try {
    await apiFetch(`/expense/${expenseId}`, {
      method: "DELETE"
    });

    setMessage($("globalMessage"), "Expense deleted successfully.", true);
    await Promise.all([loadExpenses(), loadSummary(), loadCategorySummary()]);

    // If the current page became empty after delete, move back one page when possible.
    const listText = $("expenseList").textContent.trim();
    if (listText === "No expenses found." && page > 1) {
      page -= 1;
      await loadExpenses();
    }
  } catch (error) {
    setMessage($("globalMessage"), error.message);
  }
}

function openEditModal(expense) {
  $("editTitle").value = expense.title;
  $("editAmount").value = expense.amount;
  $("editCategory").value = expense.category;
  $("editDescription").value = expense.description || "";
  $("editExpenseDate").value = expense.expense_date;
  $("editForm").dataset.expenseId = expense.id;

  setMessage($("editMessage"), "");
  $("editModal").classList.remove("hidden");
}

function closeEditModal() {
  $("editModal").classList.add("hidden");
  $("editForm").reset();
  delete $("editForm").dataset.expenseId;
  setMessage($("editMessage"), "");
}

async function editExpense(expenseId) {
  try {
    const expense = await apiFetch(`/expense/${expenseId}`);
    openEditModal(expense);
  } catch (error) {
    setMessage($("globalMessage"), error.message);
  }
}

async function saveEditedExpense(event) {
  event.preventDefault();

  const expenseId = $("editForm").dataset.expenseId;

  try {
    const payload = {
      title: $("editTitle").value.trim(),
      amount: Number($("editAmount").value),
      category: $("editCategory").value,
      description: $("editDescription").value.trim() || null,
      expense_date: $("editExpenseDate").value
    };

    await apiFetch(`/expense/${expenseId}`, {
      method: "PATCH",
      body: JSON.stringify(payload)
    });

    closeEditModal();
    setMessage($("globalMessage"), "Expense updated successfully.", true);
    await Promise.all([loadExpenses(), loadSummary(), loadCategorySummary()]);
  } catch (error) {
    setMessage($("editMessage"), error.message);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

$("loginTab").addEventListener("click", showLoginMode);
$("registerTab").addEventListener("click", showRegisterMode);
authForm.addEventListener("submit", handleAuth);
$("logoutBtn").addEventListener("click", logout);

$("expenseForm").addEventListener("submit", addExpense);

$("expenseList").addEventListener("click", async (event) => {
  const editButton = event.target.closest(".edit-btn");
  const deleteButton = event.target.closest(".delete-btn");

  if (editButton) {
    await editExpense(editButton.dataset.id);
  }

  if (deleteButton) {
    await deleteExpense(deleteButton.dataset.id);
  }
});

$("editForm").addEventListener("submit", saveEditedExpense);
$("closeEditBtn").addEventListener("click", closeEditModal);
$("cancelEditBtn").addEventListener("click", closeEditModal);

$("applyFilters").addEventListener("click", async () => {
  page = 1;
  await loadExpenses();
});

$("clearFilters").addEventListener("click", async () => {
  $("filterCategory").value = "";
  $("minAmount").value = "";
  $("maxAmount").value = "";
  page = 1;
  await loadExpenses();
});

$("refreshBtn").addEventListener("click", async () => {
  await Promise.all([loadExpenses(), loadSummary(), loadCategorySummary()]);
});

$("prevBtn").addEventListener("click", async () => {
  if (page > 1) {
    page -= 1;
    await loadExpenses();
  }
});

$("nextBtn").addEventListener("click", async () => {
  if (!$("nextBtn").disabled) {
    page += 1;
    await loadExpenses();
  }
});

const today = new Date().toISOString().split("T")[0];
$("expenseDate").value = today;

// Always start with an unfiltered list.
$("filterCategory").value = "";
$("minAmount").value = "";
$("maxAmount").value = "";

if (token) {
  loadApp();
} else {
  showLoginMode();
}
