/**
 * AcademiaPulse - Student Record Management System
 * Frontend Application Controller & API Integration
 */

// Application State
const state = {
  students: [],
  stats: null,
  currentView: localStorage.getItem('academiapulse_view') || 'table',
  theme: localStorage.getItem('academiapulse_theme') || 'dark',
  filters: {
    search: '',
    department: 'All',
    status: 'All',
    sort_by: 'id',
    order: 'desc'
  },
  editingId: null,
  deleteTarget: null
};

// ==========================================================================
// API Client
// ==========================================================================
const api = {
  async getStats() {
    const res = await fetch('/api/stats');
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to fetch stats');
    return data.data;
  },

  async getStudents(params = {}) {
    const query = new URLSearchParams();
    if (params.search) query.append('search', params.search);
    if (params.department && params.department !== 'All') query.append('department', params.department);
    if (params.status && params.status !== 'All') query.append('status', params.status);
    if (params.sort_by) query.append('sort_by', params.sort_by);
    if (params.order) query.append('order', params.order);

    const res = await fetch(`/api/students?${query.toString()}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to fetch students');
    return data.data;
  },

  async getStudent(id) {
    const res = await fetch(`/api/students/${id}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Student not found');
    return data.data;
  },

  async getNextId() {
    const res = await fetch('/api/next-id');
    const data = await res.json();
    return data.next_id;
  },

  async createStudent(payload) {
    const res = await fetch('/api/students', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw data;
    return data;
  },

  async updateStudent(id, payload) {
    const res = await fetch(`/api/students/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok) throw data;
    return data;
  },

  async deleteStudent(id) {
    const res = await fetch(`/api/students/${id}`, { method: 'DELETE' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to delete student');
    return data;
  },

  async resetSeedData() {
    const res = await fetch('/api/seed', { method: 'POST' });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to reset seed data');
    return data;
  }
};

// ==========================================================================
// UI Helpers & Utilities
// ==========================================================================
function getInitials(firstName, lastName) {
  const f = firstName ? firstName.charAt(0).toUpperCase() : '';
  const l = lastName ? lastName.charAt(0).toUpperCase() : '';
  return `${f}${l}` || 'ST';
}

function getGpaClass(gpa) {
  const val = parseFloat(gpa);
  if (val >= 3.8) return 'gpa-excellent';
  if (val >= 3.5) return 'gpa-good';
  if (val >= 3.0) return 'gpa-average';
  return 'gpa-probation';
}

function getStatusClass(status) {
  switch (status) {
    case 'Active': return 'status-active';
    case 'On Leave': return 'status-on-leave';
    case 'Graduated': return 'status-graduated';
    default: return 'status-inactive';
  }
}

function getGpaHonorLabel(gpa) {
  const val = parseFloat(gpa);
  if (val >= 3.9) return "Summa Cum Laude / Dean's List";
  if (val >= 3.7) return "Magna Cum Laude";
  if (val >= 3.5) return "Cum Laude / Honors";
  if (val >= 3.0) return "Good Standing";
  return "Academic Advisory";
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Toast System
function showToast(title, message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconMap = {
    success: 'fas fa-check-circle',
    danger: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle',
    warning: 'fas fa-exclamation-circle'
  };

  toast.innerHTML = `
    <i class="${iconMap[type] || iconMap.info} toast-icon"></i>
    <div class="toast-content">
      <div class="toast-title">${escapeHtml(title)}</div>
      <div class="toast-message">${escapeHtml(message)}</div>
    </div>
    <button class="toast-close" aria-label="Close">&times;</button>
    <div class="toast-progress"></div>
  `;

  container.appendChild(toast);

  // Trigger animation
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  const closeToast = () => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 350);
  };

  toast.querySelector('.toast-close').addEventListener('click', closeToast);
  setTimeout(closeToast, duration);
}

// ==========================================================================
// Renderers
// ==========================================================================
function renderStats(stats) {
  if (!stats) return;
  document.getElementById('statTotalStudents').textContent = stats.total_students || 0;
  document.getElementById('statActiveStudents').textContent = stats.active_count || 0;
  document.getElementById('statAverageGpa').textContent = stats.average_gpa !== null ? stats.average_gpa.toFixed(2) : '0.00';
  
  const deptsCount = stats.department_breakdown ? stats.department_breakdown.length : 0;
  document.getElementById('statDepartmentsCount').textContent = deptsCount;

  // Subtext updates
  const activeRate = stats.total_students ? Math.round((stats.active_count / stats.total_students) * 100) : 0;
  document.getElementById('statActiveRate').textContent = `${activeRate}% of roster`;
  document.getElementById('statHonorRoll').textContent = `${stats.honor_roll_count || 0} Honor Roll`;
}

function renderStudentsList() {
  const container = document.getElementById('studentsContainer');
  const countEl = document.getElementById('resultsCount');
  const emptyEl = document.getElementById('emptyState');

  countEl.textContent = `Showing ${state.students.length} student${state.students.length === 1 ? '' : 's'}`;

  if (state.students.length === 0) {
    container.innerHTML = '';
    emptyEl.style.display = 'flex';
    return;
  }
  emptyEl.style.display = 'none';

  if (state.currentView === 'table') {
    renderTableView(container);
  } else {
    renderGridView(container);
  }
}

function renderTableView(container) {
  const html = `
    <div class="table-wrapper">
      <table class="data-table" id="studentsTable">
        <thead>
          <tr>
            <th>Student ID</th>
            <th class="sortable" onclick="handleSortChange('name')">Student Name <i class="fas fa-sort"></i></th>
            <th class="sortable" onclick="handleSortChange('department')">Department <i class="fas fa-sort"></i></th>
            <th>Year Level</th>
            <th class="sortable" onclick="handleSortChange('gpa')">GPA <i class="fas fa-sort"></i></th>
            <th class="sortable" onclick="handleSortChange('status')">Status <i class="fas fa-sort"></i></th>
            <th style="text-align: right;">Actions</th>
          </tr>
        </thead>
        <tbody>
          ${state.students.map(s => `
            <tr>
              <td>
                <span class="student-id-pill">${escapeHtml(s.student_id)}</span>
              </td>
              <td>
                <div class="student-info-cell">
                  <div class="avatar">${getInitials(s.first_name, s.last_name)}</div>
                  <div class="student-meta">
                    <span class="student-name" onclick="openDetailsModal(${s.id})">
                      ${escapeHtml(s.first_name)} ${escapeHtml(s.last_name)}
                    </span>
                    <span class="student-email">${escapeHtml(s.email)}</span>
                  </div>
                </div>
              </td>
              <td>
                <span class="dept-badge">${escapeHtml(s.department)}</span>
              </td>
              <td>
                <span style="font-weight: 500;">${escapeHtml(s.year_level)}</span>
              </td>
              <td>
                <span class="gpa-badge ${getGpaClass(s.gpa)}">
                  <i class="fas fa-chart-line"></i> ${Number(s.gpa).toFixed(2)}
                </span>
              </td>
              <td>
                <span class="status-pill ${getStatusClass(s.status)}">
                  <span class="status-dot"></span>
                  ${escapeHtml(s.status)}
                </span>
              </td>
              <td>
                <div class="actions-cell" style="justify-content: flex-end;">
                  <button class="action-btn view-action" title="View Details" onclick="openDetailsModal(${s.id})">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="action-btn edit-action" title="Edit Record" onclick="openEditModal(${s.id})">
                    <i class="fas fa-pen"></i>
                  </button>
                  <button class="action-btn delete-action" title="Delete Record" onclick="openDeleteModal(${s.id}, '${escapeHtml(s.first_name)} ${escapeHtml(s.last_name)}', '${escapeHtml(s.student_id)}')">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
  container.innerHTML = html;
}

function renderGridView(container) {
  const html = `
    <div class="cards-grid">
      ${state.students.map(s => `
        <div class="student-card">
          <div class="card-header-row">
            <div class="card-avatar-meta">
              <div class="avatar">${getInitials(s.first_name, s.last_name)}</div>
              <div>
                <h3 class="card-student-name" onclick="openDetailsModal(${s.id})">
                  ${escapeHtml(s.first_name)} ${escapeHtml(s.last_name)}
                </h3>
                <span class="student-id-pill" style="margin-top: 0.25rem;">${escapeHtml(s.student_id)}</span>
              </div>
            </div>
            <span class="status-pill ${getStatusClass(s.status)}">
              <span class="status-dot"></span>
              ${escapeHtml(s.status)}
            </span>
          </div>

          <div class="card-body">
            <div class="card-detail-item">
              <span class="card-detail-label"><i class="fas fa-graduation-cap"></i> Department</span>
              <span class="card-detail-value" style="font-size: 0.8rem;">${escapeHtml(s.department)}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-label"><i class="fas fa-layer-group"></i> Level</span>
              <span class="card-detail-value">${escapeHtml(s.year_level)}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-label"><i class="fas fa-star"></i> GPA</span>
              <span class="gpa-badge ${getGpaClass(s.gpa)}">${Number(s.gpa).toFixed(2)}</span>
            </div>
            <div class="card-detail-item">
              <span class="card-detail-label"><i class="fas fa-envelope"></i> Email</span>
              <span class="card-detail-value" style="font-size: 0.78rem; max-width: 170px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                ${escapeHtml(s.email)}
              </span>
            </div>
          </div>

          <div class="card-footer">
            <span style="font-size: 0.75rem; color: var(--text-muted);">
              <i class="fas fa-phone"></i> ${escapeHtml(s.phone)}
            </span>
            <div class="actions-cell">
              <button class="action-btn view-action" title="View Details" onclick="openDetailsModal(${s.id})">
                <i class="fas fa-eye"></i>
              </button>
              <button class="action-btn edit-action" title="Edit Record" onclick="openEditModal(${s.id})">
                <i class="fas fa-pen"></i>
              </button>
              <button class="action-btn delete-action" title="Delete Record" onclick="openDeleteModal(${s.id}, '${escapeHtml(s.first_name)} ${escapeHtml(s.last_name)}', '${escapeHtml(s.student_id)}')">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </div>
      `).join('')}
    </div>
  `;
  container.innerHTML = html;
}

// ==========================================================================
// Modal Operations
// ==========================================================================
function closeModals() {
  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.classList.remove('active');
  });
  state.editingId = null;
  state.deleteTarget = null;
  clearFormErrors();
}

function clearFormErrors() {
  document.querySelectorAll('.field-error-msg').forEach(el => {
    el.textContent = '';
    el.classList.remove('visible');
  });
  document.querySelectorAll('.input-control, .textarea-control').forEach(el => {
    el.classList.remove('error');
  });
}

function setFieldError(field, message) {
  const errorEl = document.getElementById(`err_${field}`);
  const inputEl = document.getElementById(`field_${field}`);
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add('visible');
  }
  if (inputEl) {
    inputEl.classList.add('error');
  }
}

// Add New Student Modal
async function openAddModal() {
  closeModals();
  const form = document.getElementById('studentForm');
  form.reset();
  clearFormErrors();
  state.editingId = null;

  document.getElementById('modalTitle').textContent = 'Add New Student Record';
  document.getElementById('modalSubtitle').textContent = 'Enter student academic, personal, and contact information';
  document.getElementById('submitBtnText').textContent = '+ Add Student';
  const submitIcon = document.getElementById('submitBtnIcon');
  if (submitIcon) submitIcon.className = 'fas fa-user-plus';

  // GPA Slider initialization
  document.getElementById('field_gpa').value = '3.50';
  document.getElementById('field_gpa_slider').value = '3.50';
  document.getElementById('gpaSliderValue').textContent = '3.50';

  // Pre-fetch next student ID
  try {
    const nextId = await api.getNextId();
    document.getElementById('field_student_id').value = nextId;
  } catch (e) {
    console.warn('Could not auto-generate student ID', e);
  }

  document.getElementById('studentModal').classList.add('active');
  document.getElementById('field_first_name').focus();
}

// Edit Existing Student Modal
async function openEditModal(id) {
  closeModals();
  clearFormErrors();
  state.editingId = id;

  document.getElementById('modalTitle').textContent = 'Edit Student Record';
  document.getElementById('modalSubtitle').textContent = 'Update student details and save changes';
  document.getElementById('submitBtnText').textContent = 'Update Student';
  const editSubmitIcon = document.getElementById('submitBtnIcon');
  if (editSubmitIcon) editSubmitIcon.className = 'fas fa-check';

  try {
    const student = await api.getStudent(id);

    document.getElementById('field_student_id').value = student.student_id;
    document.getElementById('field_first_name').value = student.first_name;
    document.getElementById('field_last_name').value = student.last_name;
    document.getElementById('field_email').value = student.email;
    document.getElementById('field_phone').value = student.phone;
    document.getElementById('field_department').value = student.department;
    document.getElementById('field_year_level').value = student.year_level;
    document.getElementById('field_gpa').value = Number(student.gpa).toFixed(2);
    document.getElementById('field_gpa_slider').value = student.gpa;
    document.getElementById('gpaSliderValue').textContent = Number(student.gpa).toFixed(2);
    document.getElementById('field_status').value = student.status;
    document.getElementById('field_date_of_birth').value = student.date_of_birth || '';
    document.getElementById('field_gender').value = student.gender || '';
    document.getElementById('field_address').value = student.address || '';
    document.getElementById('field_emergency_contact').value = student.emergency_contact || '';
    document.getElementById('field_notes').value = student.notes || '';

    document.getElementById('studentModal').classList.add('active');
  } catch (err) {
    showToast('Error', err.message || 'Could not load student information', 'danger');
  }
}

// View Student Details Modal
async function openDetailsModal(id) {
  closeModals();
  try {
    const student = await api.getStudent(id);

    document.getElementById('detailsAvatar').textContent = getInitials(student.first_name, student.last_name);
    document.getElementById('detailsName').textContent = `${student.first_name} ${student.last_name}`;
    document.getElementById('detailsStudentId').textContent = student.student_id;
    
    const statusPill = document.getElementById('detailsStatus');
    statusPill.className = `status-pill ${getStatusClass(student.status)}`;
    statusPill.innerHTML = `<span class="status-dot"></span> ${escapeHtml(student.status)}`;

    document.getElementById('detailsEmail').textContent = student.email;
    document.getElementById('detailsPhone').textContent = student.phone;
    document.getElementById('detailsDept').textContent = student.department;
    document.getElementById('detailsYear').textContent = student.year_level;
    
    const gpaEl = document.getElementById('detailsGpa');
    gpaEl.className = `gpa-badge ${getGpaClass(student.gpa)}`;
    gpaEl.innerHTML = `<i class="fas fa-chart-line"></i> ${Number(student.gpa).toFixed(2)} &mdash; ${getGpaHonorLabel(student.gpa)}`;

    document.getElementById('detailsDob').textContent = student.date_of_birth || 'Not Specified';
    document.getElementById('detailsGender').textContent = student.gender || 'Not Specified';
    document.getElementById('detailsAddress').textContent = student.address || 'No residential address on file.';
    document.getElementById('detailsEmergency').textContent = student.emergency_contact || 'None recorded.';
    document.getElementById('detailsNotes').textContent = student.notes || 'No advisor remarks recorded.';
    document.getElementById('detailsCreatedAt').textContent = student.created_at ? new Date(student.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Unknown';

    // Modal Action buttons handlers
    document.getElementById('detailsEditBtn').onclick = () => openEditModal(student.id);
    document.getElementById('detailsDeleteBtn').onclick = () => openDeleteModal(student.id, `${student.first_name} ${student.last_name}`, student.student_id);

    document.getElementById('detailsModal').classList.add('active');
  } catch (err) {
    showToast('Error', err.message || 'Could not load student details', 'danger');
  }
}

// Delete Confirmation Modal
function openDeleteModal(id, name, studentId) {
  closeModals();
  state.deleteTarget = { id, name, studentId };
  document.getElementById('deleteTargetName').textContent = `${name} (${studentId})`;
  document.getElementById('deleteModal').classList.add('active');
}

// ==========================================================================
// Event Listeners & Actions
// ==========================================================================
async function reloadData() {
  try {
    const [students, stats] = await Promise.all([
      api.getStudents(state.filters),
      api.getStats()
    ]);
    state.students = students;
    state.stats = stats;
    renderStats(stats);
    renderStudentsList();
  } catch (err) {
    showToast('Data Error', err.message || 'Failed to reload students data', 'danger');
  }
}

// Form Submission (Add or Update)
async function handleFormSubmit(e) {
  e.preventDefault();
  clearFormErrors();

  const payload = {
    student_id: document.getElementById('field_student_id').value.trim(),
    first_name: document.getElementById('field_first_name').value.trim(),
    last_name: document.getElementById('field_last_name').value.trim(),
    email: document.getElementById('field_email').value.trim(),
    phone: document.getElementById('field_phone').value.trim(),
    department: document.getElementById('field_department').value.trim(),
    year_level: document.getElementById('field_year_level').value.trim(),
    gpa: parseFloat(document.getElementById('field_gpa').value),
    status: document.getElementById('field_status').value.trim(),
    date_of_birth: document.getElementById('field_date_of_birth').value.trim(),
    gender: document.getElementById('field_gender').value.trim(),
    address: document.getElementById('field_address').value.trim(),
    emergency_contact: document.getElementById('field_emergency_contact').value.trim(),
    notes: document.getElementById('field_notes').value.trim()
  };

  // Local basic checks
  let hasClientErrors = false;
  if (!payload.first_name) { setFieldError('first_name', 'First name is required'); hasClientErrors = true; }
  if (!payload.last_name) { setFieldError('last_name', 'Last name is required'); hasClientErrors = true; }
  if (!payload.email) { setFieldError('email', 'Email address is required'); hasClientErrors = true; }
  if (!payload.phone) { setFieldError('phone', 'Phone number is required'); hasClientErrors = true; }
  if (!payload.department) { setFieldError('department', 'Department is required'); hasClientErrors = true; }
  if (!payload.year_level) { setFieldError('year_level', 'Year level is required'); hasClientErrors = true; }
  if (isNaN(payload.gpa) || payload.gpa < 0 || payload.gpa > 4.0) {
    setFieldError('gpa', 'GPA must be between 0.00 and 4.00');
    hasClientErrors = true;
  }

  if (hasClientErrors) return;

  const submitBtn = document.getElementById('submitStudentBtn');
  const originalBtnHtml = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<span class="spinner"></span> ' + (state.editingId ? 'Updating...' : 'Adding...');

  try {
    let result;
    if (state.editingId) {
      result = await api.updateStudent(state.editingId, payload);
      showToast('Record Updated', result.message || 'Student record updated successfully', 'success');
    } else {
      result = await api.createStudent(payload);
      showToast('Student Added', result.message || 'New student added successfully', 'success');
    }
    closeModals();
    await reloadData();
  } catch (err) {
    if (err.errors) {
      for (const [field, msg] of Object.entries(err.errors)) {
        setFieldError(field, msg);
      }
      showToast('Validation Failed', 'Please review the highlighted errors.', 'warning');
    } else {
      showToast('Error', err.error || err.message || 'Failed to save student', 'danger');
    }
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalBtnHtml;
  }
}

// Delete Confirmation
async function handleConfirmDelete() {
  if (!state.deleteTarget) return;

  const confirmBtn = document.getElementById('confirmDeleteBtn');
  const origText = confirmBtn.textContent;
  confirmBtn.disabled = true;
  confirmBtn.innerHTML = '<span class="spinner"></span> Deleting...';

  try {
    const res = await api.deleteStudent(state.deleteTarget.id);
    showToast('Deleted', res.message || 'Student deleted successfully', 'success');
    closeModals();
    await reloadData();
  } catch (err) {
    showToast('Delete Failed', err.message || 'Could not delete student', 'danger');
  } finally {
    confirmBtn.disabled = false;
    confirmBtn.textContent = origText;
  }
}

// Sorting
function handleSortChange(column) {
  if (state.filters.sort_by === column) {
    state.filters.order = state.filters.order === 'asc' ? 'desc' : 'asc';
  } else {
    state.filters.sort_by = column;
    state.filters.order = (column === 'gpa' || column === 'id') ? 'desc' : 'asc';
  }
  document.getElementById('sortSelect').value = `${state.filters.sort_by}_${state.filters.order}`;
  reloadData();
}

// Search debouncer
let searchTimeout = null;
function handleSearchInput(e) {
  const query = e.target.value;
  state.filters.search = query;

  const clearBtn = document.getElementById('searchClearBtn');
  if (query.trim().length > 0) {
    clearBtn.classList.add('visible');
  } else {
    clearBtn.classList.remove('visible');
  }

  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    reloadData();
  }, 250);
}

function handleSearchClear() {
  const searchInput = document.getElementById('globalSearchInput');
  searchInput.value = '';
  state.filters.search = '';
  document.getElementById('searchClearBtn').classList.remove('visible');
  reloadData();
  searchInput.focus();
}

// View mode toggle
function setViewMode(mode) {
  state.currentView = mode;
  localStorage.setItem('academiapulse_view', mode);

  document.getElementById('viewTableBtn').classList.toggle('active', mode === 'table');
  document.getElementById('viewGridBtn').classList.toggle('active', mode === 'grid');
  renderStudentsList();
}

// Theme toggle
function setTheme(theme) {
  state.theme = theme;
  localStorage.setItem('academiapulse_theme', theme);
  document.documentElement.setAttribute('data-theme', theme);
  
  const icon = document.getElementById('themeToggleIcon');
  if (theme === 'light') {
    icon.className = 'fas fa-sun';
  } else {
    icon.className = 'fas fa-moon';
  }
}

function toggleTheme() {
  const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
  setTheme(nextTheme);
}

// Restore Sample Data
async function handleResetData() {
  if (!confirm('Are you sure you want to reset all records back to the original demo dataset? Any custom additions will be replaced.')) {
    return;
  }
  try {
    await api.resetSeedData();
    showToast('Database Reset', 'Sample student dataset restored successfully.', 'success');
    await reloadData();
  } catch (err) {
    showToast('Reset Failed', err.message || 'Failed to reset sample data', 'danger');
  }
}

// Sync GPA slider and input
function setupGpaSync() {
  const gpaInput = document.getElementById('field_gpa');
  const gpaSlider = document.getElementById('field_gpa_slider');
  const gpaPreview = document.getElementById('gpaSliderValue');

  gpaSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value).toFixed(2);
    gpaInput.value = val;
    gpaPreview.textContent = val;
  });

  gpaInput.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val) && val >= 0 && val <= 4.0) {
      gpaSlider.value = val;
      gpaPreview.textContent = val.toFixed(2);
    }
  });
}

// Export CSV handler
function handleExportCsv() {
  window.location.href = '/api/export/csv';
  showToast('Export Started', 'Student records CSV is downloading...', 'info');
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
  window.addEventListener('keydown', (e) => {
    // Focus search on '/' or 'Ctrl+K'
    if ((e.key === '/' || (e.ctrlKey && e.key.toLowerCase() === 'k')) && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      document.getElementById('globalSearchInput').focus();
    }
    // Close modals on ESC
    if (e.key === 'Escape') {
      closeModals();
    }
  });
}

// ==========================================================================
// Initialization on DOMContentLoaded
// ==========================================================================
document.addEventListener('DOMContentLoaded', () => {
  // Apply initial theme
  setTheme(state.theme);

  // Apply initial view mode
  setViewMode(state.currentView);

  // Event Listeners for Filters & Toolbar
  document.getElementById('globalSearchInput').addEventListener('input', handleSearchInput);
  document.getElementById('searchClearBtn').addEventListener('click', handleSearchClear);

  document.getElementById('departmentFilter').addEventListener('change', (e) => {
    state.filters.department = e.target.value;
    reloadData();
  });

  document.getElementById('sortSelect').addEventListener('change', (e) => {
    const [sort_by, order] = e.target.value.split('_');
    state.filters.sort_by = sort_by;
    state.filters.order = order;
    reloadData();
  });

  // Status Filter Pills
  document.querySelectorAll('.status-filter-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.status-filter-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.filters.status = pill.getAttribute('data-status');
      reloadData();
    });
  });

  // View Switchers
  document.getElementById('viewTableBtn').addEventListener('click', () => setViewMode('table'));
  document.getElementById('viewGridBtn').addEventListener('click', () => setViewMode('grid'));

  // Header Actions
  document.getElementById('themeToggleBtn').addEventListener('click', toggleTheme);
  document.getElementById('addStudentBtn').addEventListener('click', openAddModal);
  document.getElementById('emptyAddBtn').addEventListener('click', openAddModal);
  document.getElementById('exportCsvBtn').addEventListener('click', handleExportCsv);
  document.getElementById('resetDataBtn').addEventListener('click', handleResetData);

  // Modal Closures
  document.querySelectorAll('.modal-close-btn, .modal-cancel-btn').forEach(btn => {
    btn.addEventListener('click', closeModals);
  });
  document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) closeModals();
    });
  });

  // Form Submissions
  document.getElementById('studentForm').addEventListener('submit', handleFormSubmit);
  document.getElementById('confirmDeleteBtn').addEventListener('click', handleConfirmDelete);

  // Details Modal Print button
  document.getElementById('detailsPrintBtn').addEventListener('click', () => {
    window.print();
  });

  // Setup helpers
  setupGpaSync();
  setupKeyboardShortcuts();

  // Load initial data
  reloadData();
});
