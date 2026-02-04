/**
 * Employee Management System - Frontend Application
 * Modern JavaScript with API integration
 */

// ========================================
// Configuration & State
// ========================================
const API_BASE = '/api';
let authToken = localStorage.getItem('token');
let currentUser = null;
let currentPage = {
    employees: 1,
    departments: 1,
    projects: 1,
    tasks: 1
};

// ========================================
// Utility Functions
// ========================================

/**
 * Make API request with authentication
 */
async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(authToken && { 'Authorization': `Bearer ${authToken}` }),
        ...options.headers
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });

        if (response.status === 401) {
            logout();
            throw new Error('Session expired. Please login again.');
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Request failed');
        }

        if (response.status === 204) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    
    toast.className = `toast ${type}`;
    toastMessage.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Show/hide loading overlay
 */
function setLoading(show) {
    document.getElementById('loading-overlay').style.display = show ? 'flex' : 'none';
}

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

/**
 * Get initials from name
 */
function getInitials(name) {
    return name
        .split(' ')
        .map(word => word[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
}

/**
 * Check if date is overdue
 */
function isOverdue(dateStr) {
    if (!dateStr) return false;
    return new Date(dateStr) < new Date();
}

// ========================================
// Authentication Functions
// ========================================

/**
 * Fill demo credentials
 */
function fillCredentials(email, password) {
    document.getElementById('email').value = email;
    document.getElementById('password').value = password;
}

/**
 * Toggle password visibility
 */
function togglePassword() {
    const passwordInput = document.getElementById('password');
    const icon = document.querySelector('.toggle-password i');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

/**
 * Handle login form submission
 */
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('login-error');
    
    setLoading(true);
    errorDiv.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Store token and user info
        authToken = data.access_token;
        currentUser = data.user;
        localStorage.setItem('token', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));
        
        // Show main app
        showApp();
        showToast('Login successful!', 'success');
        
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    } finally {
        setLoading(false);
    }
});

/**
 * Logout user
 */
function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    
    document.getElementById('login-page').classList.add('active');
    document.getElementById('app-page').classList.remove('active');
    
    // Clear form
    document.getElementById('login-form').reset();
}

/**
 * Check authentication on page load
 */
function checkAuth() {
    const storedUser = localStorage.getItem('user');
    
    if (authToken && storedUser) {
        currentUser = JSON.parse(storedUser);
        showApp();
    } else {
        document.getElementById('login-page').classList.add('active');
    }
}

/**
 * Show main application
 */
function showApp() {
    document.getElementById('login-page').classList.remove('active');
    document.getElementById('app-page').classList.add('active');
    
    // Update user info in header
    document.getElementById('user-name').textContent = currentUser.full_name;
    document.getElementById('user-role').textContent = currentUser.role;
    
    // Setup role-based access
    setupRoleBasedAccess();
    
    // Load initial data
    loadDashboard();
}

/**
 * Setup role-based access controls
 */
function setupRoleBasedAccess() {
    const isAdmin = currentUser.role === 'admin';
    const isManager = currentUser.role === 'manager';
    const isEmployee = currentUser.role === 'employee';
    
    // Hide add buttons for employees
    document.getElementById('btn-add-employee').style.display = isAdmin ? 'flex' : 'none';
    document.getElementById('btn-add-department').style.display = isAdmin ? 'flex' : 'none';
    document.getElementById('btn-add-project').style.display = (isAdmin || isManager) ? 'flex' : 'none';
    document.getElementById('btn-add-task').style.display = (isAdmin || isManager) ? 'flex' : 'none';
    
    // Hide certain nav items for employees
    if (isEmployee) {
        document.getElementById('nav-employees').style.display = 'none';
        document.getElementById('nav-departments').style.display = 'none';
    }
}

// ========================================
// Navigation Functions
// ========================================

/**
 * Toggle sidebar on mobile
 */
function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('open');
}

/**
 * Show specific section
 */
function showSection(sectionName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`)?.classList.add('active');
    
    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        employees: 'Employees',
        departments: 'Departments',
        projects: 'Projects',
        tasks: 'Tasks'
    };
    document.getElementById('page-title').textContent = titles[sectionName] || 'Dashboard';
    
    // Show section
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    // Load section data
    switch (sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'employees':
            loadEmployees();
            break;
        case 'departments':
            loadDepartments();
            break;
        case 'projects':
            loadProjects();
            break;
        case 'tasks':
            loadTasks();
            break;
    }
    
    // Close sidebar on mobile
    document.querySelector('.sidebar').classList.remove('open');
}

// Setup navigation click handlers
document.querySelectorAll('.nav-item[data-section]').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        showSection(item.dataset.section);
    });
});

// ========================================
// Dashboard Functions
// ========================================

async function loadDashboard() {
    try {
        // Load statistics
        const [employees, departments, projects, taskStats] = await Promise.all([
            apiRequest('/employees?page_size=1'),
            apiRequest('/departments?page_size=1'),
            apiRequest('/projects?page_size=1'),
            apiRequest('/tasks/stats?my_stats=' + (currentUser.role === 'employee'))
        ]);
        
        document.getElementById('stat-employees').textContent = employees.total || 0;
        document.getElementById('stat-departments').textContent = departments.total || 0;
        document.getElementById('stat-projects').textContent = projects.total || 0;
        document.getElementById('stat-tasks').textContent = taskStats.total || 0;
        
        // Update task overview
        updateTaskOverview(taskStats);
        
        // Load recent tasks
        loadRecentTasks();
        
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error loading dashboard', 'error');
    }
}

function updateTaskOverview(stats) {
    const total = stats.total || 1;
    
    document.getElementById('tasks-assigned').textContent = stats.assigned || 0;
    document.getElementById('tasks-progress').textContent = stats.in_progress || 0;
    document.getElementById('tasks-completed').textContent = stats.completed || 0;
    document.getElementById('tasks-overdue').textContent = stats.overdue || 0;
    
    document.getElementById('progress-assigned').style.width = `${(stats.assigned / total) * 100}%`;
    document.getElementById('progress-in-progress').style.width = `${(stats.in_progress / total) * 100}%`;
    document.getElementById('progress-completed').style.width = `${(stats.completed / total) * 100}%`;
    document.getElementById('progress-overdue').style.width = `${(stats.overdue / total) * 100}%`;
}

async function loadRecentTasks() {
    try {
        const myTasks = currentUser.role === 'employee';
        const tasks = await apiRequest(`/tasks?page_size=5&my_tasks=${myTasks}`);
        
        const container = document.getElementById('recent-tasks-list');
        
        if (!tasks.tasks || tasks.tasks.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-tasks"></i>
                    <h3>No tasks yet</h3>
                    <p>Tasks will appear here when assigned</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = tasks.tasks.map(task => `
            <div class="task-item" onclick="showTaskDetail(${task.id})">
                <span class="task-status-dot ${task.status}"></span>
                <div class="task-item-info">
                    <div class="task-item-title">${escapeHtml(task.title)}</div>
                    <div class="task-item-meta">
                        <span>${formatDate(task.due_date)}</span>
                    </div>
                </div>
                <span class="priority-badge ${task.priority}">${task.priority}</span>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading recent tasks:', error);
    }
}

// ========================================
// Employees Functions
// ========================================

async function loadEmployees(page = 1) {
    try {
        setLoading(true);
        currentPage.employees = page;
        
        const search = document.getElementById('employee-search')?.value || '';
        const department = document.getElementById('employee-department-filter')?.value || '';
        const status = document.getElementById('employee-status-filter')?.value || '';
        
        let url = `/employees?page=${page}&page_size=10`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (department) url += `&department_id=${department}`;
        if (status) url += `&is_active=${status}`;
        
        const data = await apiRequest(url);
        
        renderEmployeesTable(data.employees);
        renderPagination('employees', data.page, data.total_pages);
        
        // Load department filter options
        loadDepartmentOptions();
        
    } catch (error) {
        console.error('Error loading employees:', error);
        showToast('Error loading employees', 'error');
    } finally {
        setLoading(false);
    }
}

function renderEmployeesTable(employees) {
    const tbody = document.getElementById('employees-table-body');
    
    if (!employees || employees.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <i class="fas fa-users"></i>
                    <h3>No employees found</h3>
                    <p>Add employees to get started</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = employees.map(emp => `
        <tr>
            <td>
                <div class="employee-cell">
                    <div class="employee-avatar">${getInitials(emp.first_name + ' ' + emp.last_name)}</div>
                    <div>
                        <div class="employee-name">${escapeHtml(emp.first_name)} ${escapeHtml(emp.last_name)}</div>
                        <div class="employee-code">${escapeHtml(emp.employee_code)}</div>
                    </div>
                </div>
            </td>
            <td>${escapeHtml(emp.email)}</td>
            <td>${emp.department_id ? 'Dept #' + emp.department_id : '-'}</td>
            <td>${emp.designation || '-'}</td>
            <td>
                <span class="status-badge ${emp.is_active ? 'active' : 'inactive'}">
                    <span class="status-dot"></span>
                    ${emp.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn-icon edit" onclick="editEmployee(${emp.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    ${currentUser.role === 'admin' ? `
                        <button class="btn-icon delete" onclick="deleteEmployee(${emp.id})" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function searchEmployees() {
    clearTimeout(window.employeeSearchTimeout);
    window.employeeSearchTimeout = setTimeout(() => loadEmployees(1), 300);
}

function filterEmployees() {
    loadEmployees(1);
}

async function editEmployee(id) {
    try {
        const employee = await apiRequest(`/employees/${id}`);
        
        document.getElementById('employee-modal-title').textContent = 'Edit Employee';
        document.getElementById('employee-id').value = id;
        document.getElementById('emp-first-name').value = employee.first_name;
        document.getElementById('emp-last-name').value = employee.last_name;
        document.getElementById('emp-email').value = employee.email;
        document.getElementById('emp-phone').value = employee.phone || '';
        document.getElementById('emp-department').value = employee.department_id || '';
        document.getElementById('emp-designation').value = employee.designation || '';
        document.getElementById('emp-hire-date').value = employee.hire_date;
        document.getElementById('emp-salary').value = employee.salary || '';
        
        // Hide create account option when editing
        document.getElementById('create-account-group').style.display = 'none';
        document.getElementById('emp-password-group').style.display = 'none';
        
        showModal('employee-modal');
        
    } catch (error) {
        showToast('Error loading employee', 'error');
    }
}

async function deleteEmployee(id) {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    
    try {
        await apiRequest(`/employees/${id}`, { method: 'DELETE' });
        showToast('Employee deleted successfully');
        loadEmployees(currentPage.employees);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Employee form submission
document.getElementById('employee-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('employee-id').value;
    const data = {
        first_name: document.getElementById('emp-first-name').value,
        last_name: document.getElementById('emp-last-name').value,
        email: document.getElementById('emp-email').value,
        phone: document.getElementById('emp-phone').value || null,
        department_id: document.getElementById('emp-department').value || null,
        designation: document.getElementById('emp-designation').value || null,
        hire_date: document.getElementById('emp-hire-date').value,
        salary: document.getElementById('emp-salary').value || null
    };
    
    // Add user account creation data for new employees
    if (!id) {
        data.create_user_account = document.getElementById('emp-create-account').checked;
        if (data.create_user_account) {
            data.password = document.getElementById('emp-password').value;
        }
    }
    
    try {
        setLoading(true);
        
        if (id) {
            await apiRequest(`/employees/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showToast('Employee updated successfully');
        } else {
            await apiRequest('/employees', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Employee created successfully');
        }
        
        closeModal('employee-modal');
        loadEmployees(currentPage.employees);
        
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        setLoading(false);
    }
});

// Toggle password field visibility based on checkbox
document.getElementById('emp-create-account')?.addEventListener('change', (e) => {
    document.getElementById('emp-password-group').style.display = e.target.checked ? 'block' : 'none';
    document.getElementById('emp-password').required = e.target.checked;
});

// ========================================
// Departments Functions
// ========================================

async function loadDepartments() {
    try {
        setLoading(true);
        
        const data = await apiRequest('/departments?page_size=100');
        renderDepartmentsGrid(data.departments);
        
    } catch (error) {
        console.error('Error loading departments:', error);
        showToast('Error loading departments', 'error');
    } finally {
        setLoading(false);
    }
}

function renderDepartmentsGrid(departments) {
    const container = document.getElementById('departments-grid');
    
    if (!departments || departments.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <i class="fas fa-sitemap"></i>
                <h3>No departments yet</h3>
                <p>Create departments to organize your employees</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = departments.map(dept => `
        <div class="department-card">
            <div class="department-card-header">
                <h3>${escapeHtml(dept.name)}</h3>
                <span class="department-code">${escapeHtml(dept.code)}</span>
            </div>
            <p class="department-description">${dept.description || 'No description'}</p>
            <div class="department-stats">
                <div class="department-stat">
                    <span>-</span>
                    <small>Employees</small>
                </div>
                <div class="department-stat">
                    <span>-</span>
                    <small>Projects</small>
                </div>
            </div>
            ${currentUser.role === 'admin' ? `
                <div class="department-actions">
                    <button class="btn-icon edit" onclick="editDepartment(${dept.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon delete" onclick="deleteDepartment(${dept.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            ` : ''}
        </div>
    `).join('');
}

async function loadDepartmentOptions() {
    try {
        const data = await apiRequest('/departments?page_size=100');
        const options = data.departments.map(d => `<option value="${d.id}">${escapeHtml(d.name)}</option>`).join('');
        
        // Update all department selects
        document.querySelectorAll('#employee-department-filter, #emp-department, #proj-department').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = `<option value="">Select Department</option>${options}`;
            if (currentValue) select.value = currentValue;
        });
        
    } catch (error) {
        console.error('Error loading department options:', error);
    }
}

async function editDepartment(id) {
    try {
        const dept = await apiRequest(`/departments/${id}`);
        
        document.getElementById('department-modal-title').textContent = 'Edit Department';
        document.getElementById('department-id').value = id;
        document.getElementById('dept-name').value = dept.name;
        document.getElementById('dept-code').value = dept.code;
        document.getElementById('dept-description').value = dept.description || '';
        document.getElementById('dept-manager').value = dept.manager_id || '';
        
        await loadEmployeeOptions();
        showModal('department-modal');
        
    } catch (error) {
        showToast('Error loading department', 'error');
    }
}

async function deleteDepartment(id) {
    if (!confirm('Are you sure you want to delete this department?')) return;
    
    try {
        await apiRequest(`/departments/${id}`, { method: 'DELETE' });
        showToast('Department deleted successfully');
        loadDepartments();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Department form submission
document.getElementById('department-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('department-id').value;
    const data = {
        name: document.getElementById('dept-name').value,
        code: document.getElementById('dept-code').value,
        description: document.getElementById('dept-description').value || null,
        manager_id: document.getElementById('dept-manager').value || null
    };
    
    try {
        setLoading(true);
        
        if (id) {
            await apiRequest(`/departments/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showToast('Department updated successfully');
        } else {
            await apiRequest('/departments', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Department created successfully');
        }
        
        closeModal('department-modal');
        loadDepartments();
        
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        setLoading(false);
    }
});

// ========================================
// Projects Functions
// ========================================

async function loadProjects(page = 1) {
    try {
        setLoading(true);
        currentPage.projects = page;
        
        const search = document.getElementById('project-search')?.value || '';
        const status = document.getElementById('project-status-filter')?.value || '';
        
        let url = `/projects?page=${page}&page_size=12`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (status) url += `&status=${status}`;
        
        const data = await apiRequest(url);
        renderProjectsGrid(data.projects);
        
    } catch (error) {
        console.error('Error loading projects:', error);
        showToast('Error loading projects', 'error');
    } finally {
        setLoading(false);
    }
}

function renderProjectsGrid(projects) {
    const container = document.getElementById('projects-grid');
    
    if (!projects || projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <i class="fas fa-project-diagram"></i>
                <h3>No projects yet</h3>
                <p>Create your first project to get started</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = projects.map(proj => `
        <div class="project-card">
            <div class="project-card-header">
                <h3>${escapeHtml(proj.name)}</h3>
                <span class="project-status ${proj.status}">${proj.status.replace('_', ' ')}</span>
            </div>
            <div class="project-code">${escapeHtml(proj.code)}</div>
            <p class="project-description">${proj.description || 'No description'}</p>
            <div class="project-meta">
                <span><i class="fas fa-calendar"></i> ${formatDate(proj.start_date)}</span>
                <span><i class="fas fa-flag"></i> ${proj.priority}</span>
            </div>
            <div class="project-actions">
                ${(currentUser.role === 'admin' || currentUser.role === 'manager') ? `
                    <button class="btn-icon edit" onclick="editProject(${proj.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                ` : ''}
                ${currentUser.role === 'admin' ? `
                    <button class="btn-icon delete" onclick="deleteProject(${proj.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function searchProjects() {
    clearTimeout(window.projectSearchTimeout);
    window.projectSearchTimeout = setTimeout(() => loadProjects(1), 300);
}

function filterProjects() {
    loadProjects(1);
}

async function editProject(id) {
    try {
        const proj = await apiRequest(`/projects/${id}`);
        
        document.getElementById('project-modal-title').textContent = 'Edit Project';
        document.getElementById('project-id').value = id;
        document.getElementById('proj-name').value = proj.name;
        document.getElementById('proj-code').value = proj.code;
        document.getElementById('proj-description').value = proj.description || '';
        document.getElementById('proj-department').value = proj.department_id || '';
        document.getElementById('proj-manager').value = proj.manager_id || '';
        document.getElementById('proj-status').value = proj.status;
        document.getElementById('proj-priority').value = proj.priority;
        document.getElementById('proj-start-date').value = proj.start_date || '';
        document.getElementById('proj-end-date').value = proj.end_date || '';
        
        await Promise.all([loadDepartmentOptions(), loadEmployeeOptions()]);
        showModal('project-modal');
        
    } catch (error) {
        showToast('Error loading project', 'error');
    }
}

async function deleteProject(id) {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    try {
        await apiRequest(`/projects/${id}`, { method: 'DELETE' });
        showToast('Project deleted successfully');
        loadProjects(currentPage.projects);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Project form submission
document.getElementById('project-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('project-id').value;
    const data = {
        name: document.getElementById('proj-name').value,
        code: document.getElementById('proj-code').value,
        description: document.getElementById('proj-description').value || null,
        department_id: document.getElementById('proj-department').value || null,
        manager_id: document.getElementById('proj-manager').value || null,
        status: document.getElementById('proj-status').value,
        priority: document.getElementById('proj-priority').value,
        start_date: document.getElementById('proj-start-date').value || null,
        end_date: document.getElementById('proj-end-date').value || null
    };
    
    try {
        setLoading(true);
        
        if (id) {
            await apiRequest(`/projects/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showToast('Project updated successfully');
        } else {
            await apiRequest('/projects', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Project created successfully');
        }
        
        closeModal('project-modal');
        loadProjects(currentPage.projects);
        
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        setLoading(false);
    }
});

// ========================================
// Tasks Functions
// ========================================

async function loadTasks() {
    try {
        setLoading(true);
        
        const search = document.getElementById('task-search')?.value || '';
        const project = document.getElementById('task-project-filter')?.value || '';
        const status = document.getElementById('task-status-filter')?.value || '';
        const priority = document.getElementById('task-priority-filter')?.value || '';
        
        let url = `/tasks?page_size=100`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (project) url += `&project_id=${project}`;
        if (status) url += `&status=${status}`;
        if (priority) url += `&priority=${priority}`;
        
        const data = await apiRequest(url);
        renderTasksBoard(data.tasks);
        
        // Load project filter options
        loadProjectOptions();
        
    } catch (error) {
        console.error('Error loading tasks:', error);
        showToast('Error loading tasks', 'error');
    } finally {
        setLoading(false);
    }
}

function renderTasksBoard(tasks) {
    const assignedColumn = document.getElementById('tasks-assigned-column');
    const inProgressColumn = document.getElementById('tasks-in-progress-column');
    const completedColumn = document.getElementById('tasks-completed-column');
    
    // Clear columns
    [assignedColumn, inProgressColumn, completedColumn].forEach(col => col.innerHTML = '');
    
    // Count tasks per status
    let counts = { assigned: 0, in_progress: 0, completed: 0 };
    
    if (!tasks || tasks.length === 0) {
        assignedColumn.innerHTML = '<div class="empty-state"><p>No tasks</p></div>';
        inProgressColumn.innerHTML = '<div class="empty-state"><p>No tasks</p></div>';
        completedColumn.innerHTML = '<div class="empty-state"><p>No tasks</p></div>';
    } else {
        tasks.forEach(task => {
            const taskHtml = createTaskCard(task);
            
            switch (task.status) {
                case 'assigned':
                    assignedColumn.innerHTML += taskHtml;
                    counts.assigned++;
                    break;
                case 'in_progress':
                    inProgressColumn.innerHTML += taskHtml;
                    counts.in_progress++;
                    break;
                case 'completed':
                    completedColumn.innerHTML += taskHtml;
                    counts.completed++;
                    break;
            }
        });
    }
    
    // Update counts
    document.getElementById('count-assigned').textContent = counts.assigned;
    document.getElementById('count-in-progress').textContent = counts.in_progress;
    document.getElementById('count-completed').textContent = counts.completed;
}

function createTaskCard(task) {
    const overdueClass = task.due_date && isOverdue(task.due_date) && task.status !== 'completed' ? 'overdue' : '';
    
    return `
        <div class="task-card" onclick="showTaskDetail(${task.id})">
            <div class="task-card-header">
                <div class="task-card-title">${escapeHtml(task.title)}</div>
                <span class="priority-badge ${task.priority}">${task.priority}</span>
            </div>
            ${task.description ? `<div class="task-card-body">${escapeHtml(task.description)}</div>` : ''}
            <div class="task-card-footer">
                <div class="task-assignee">
                    <div class="task-assignee-avatar">?</div>
                    <span>Assignee</span>
                </div>
                ${task.due_date ? `
                    <div class="task-due-date ${overdueClass}">
                        <i class="fas fa-calendar"></i> ${formatDate(task.due_date)}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

function searchTasks() {
    clearTimeout(window.taskSearchTimeout);
    window.taskSearchTimeout = setTimeout(() => loadTasks(), 300);
}

function filterTasks() {
    loadTasks();
}

async function loadProjectOptions() {
    try {
        const data = await apiRequest('/projects?page_size=100');
        const options = data.projects.map(p => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join('');
        
        document.querySelectorAll('#task-project-filter, #task-project').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = `<option value="">Select Project</option>${options}`;
            if (currentValue) select.value = currentValue;
        });
        
    } catch (error) {
        console.error('Error loading project options:', error);
    }
}

async function loadEmployeeOptions() {
    try {
        const data = await apiRequest('/employees/simple');
        const options = data.map(e => `<option value="${e.id}">${escapeHtml(e.full_name)}</option>`).join('');
        
        document.querySelectorAll('#dept-manager, #proj-manager, #task-assignee').forEach(select => {
            const currentValue = select.value;
            select.innerHTML = `<option value="">Select Employee</option>${options}`;
            if (currentValue) select.value = currentValue;
        });
        
    } catch (error) {
        console.error('Error loading employee options:', error);
    }
}

async function showTaskDetail(id) {
    try {
        const task = await apiRequest(`/tasks/${id}`);
        
        document.getElementById('task-detail-title').textContent = task.title;
        
        const body = document.getElementById('task-detail-body');
        body.innerHTML = `
            <div class="task-detail-header">
                <div class="task-detail-meta">
                    <span class="status-badge ${task.status === 'completed' ? 'active' : ''}">${task.status.replace('_', ' ')}</span>
                    <span class="priority-badge ${task.priority}">${task.priority}</span>
                </div>
            </div>
            
            <div class="task-detail-section">
                <h4>Description</h4>
                <p>${task.description || 'No description provided'}</p>
            </div>
            
            <div class="task-detail-section">
                <h4>Project</h4>
                <p>${task.project_name || 'Not assigned to a project'}</p>
            </div>
            
            <div class="task-detail-section">
                <h4>Assignee</h4>
                <p>${task.assignee_name || 'Unassigned'}</p>
            </div>
            
            <div class="task-detail-section">
                <h4>Due Date</h4>
                <p>${formatDate(task.due_date)}</p>
            </div>
            
            <div class="task-detail-section">
                <h4>Progress</h4>
                <div class="progress-bar" style="height: 10px;">
                    <div class="progress completed" style="width: ${task.progress}%"></div>
                </div>
                <p style="margin-top: 0.5rem;">${task.progress}% complete</p>
            </div>
            
            ${getStatusActions(task)}
        `;
        
        showModal('task-detail-modal');
        
    } catch (error) {
        showToast('Error loading task details', 'error');
    }
}

function getStatusActions(task) {
    if (currentUser.role === 'employee') {
        // Check if task is assigned to current user
        // For simplicity, we'll show actions for all employees
    }
    
    const actions = [];
    
    switch (task.status) {
        case 'assigned':
            actions.push(`<button class="btn-status primary" onclick="updateTaskStatus(${task.id}, 'in_progress')">Start Task</button>`);
            break;
        case 'in_progress':
            actions.push(`<button class="btn-status primary" onclick="updateTaskStatus(${task.id}, 'completed')">Mark Complete</button>`);
            actions.push(`<button class="btn-status" onclick="updateTaskStatus(${task.id}, 'on_hold')">Put on Hold</button>`);
            break;
        case 'on_hold':
            actions.push(`<button class="btn-status primary" onclick="updateTaskStatus(${task.id}, 'in_progress')">Resume</button>`);
            break;
    }
    
    if (actions.length === 0) return '';
    
    return `
        <div class="task-status-actions">
            ${actions.join('')}
        </div>
    `;
}

async function updateTaskStatus(id, newStatus) {
    try {
        await apiRequest(`/tasks/${id}/status`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        });
        
        showToast('Task status updated');
        closeModal('task-detail-modal');
        loadTasks();
        loadDashboard();
        
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Task form submission
document.getElementById('task-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const id = document.getElementById('task-id').value;
    const data = {
        title: document.getElementById('task-title').value,
        description: document.getElementById('task-description').value || null,
        project_id: document.getElementById('task-project').value || null,
        assignee_id: document.getElementById('task-assignee').value || null,
        priority: document.getElementById('task-priority').value,
        due_date: document.getElementById('task-due-date').value || null,
        estimated_hours: document.getElementById('task-estimated-hours').value || null
    };
    
    try {
        setLoading(true);
        
        if (id) {
            await apiRequest(`/tasks/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showToast('Task updated successfully');
        } else {
            await apiRequest('/tasks', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Task created successfully');
        }
        
        closeModal('task-modal');
        loadTasks();
        loadDashboard();
        
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        setLoading(false);
    }
});

// ========================================
// Modal Functions
// ========================================

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
    
    // Reset form if it's a new entry
    if (modalId.includes('-modal') && !modalId.includes('detail')) {
        const form = modal.querySelector('form');
        if (form) {
            const idField = form.querySelector('input[type="hidden"]');
            if (idField && !idField.value) {
                form.reset();
            }
        }
        
        // Reset title for new entries
        const titleElement = document.getElementById(modalId.replace('-modal', '-modal-title'));
        if (titleElement && !document.getElementById(modalId.replace('-modal', '-id'))?.value) {
            const type = modalId.replace('-modal', '').replace(/-/g, ' ');
            titleElement.textContent = `Add New ${type.charAt(0).toUpperCase() + type.slice(1)}`;
        }
        
        // Load options for select fields
        if (modalId === 'employee-modal') {
            loadDepartmentOptions();
            document.getElementById('create-account-group').style.display = 'block';
        } else if (modalId === 'department-modal') {
            loadEmployeeOptions();
        } else if (modalId === 'project-modal') {
            loadDepartmentOptions();
            loadEmployeeOptions();
        } else if (modalId === 'task-modal') {
            loadProjectOptions();
            loadEmployeeOptions();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
    
    // Reset form and hidden ID
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
        const idField = form.querySelector('input[type="hidden"]');
        if (idField) idField.value = '';
    }
}

// Close modal on outside click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal(modal.id);
        }
    });
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            closeModal(modal.id);
        });
    }
});

// ========================================
// Pagination Functions
// ========================================

function renderPagination(type, currentPage, totalPages) {
    const container = document.getElementById(`${type}-pagination`);
    if (!container) return;
    
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = `
        <button onclick="load${capitalize(type)}(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 1 && i <= currentPage + 1)) {
            html += `
                <button class="${i === currentPage ? 'active' : ''}" onclick="load${capitalize(type)}(${i})">
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 2 || i === currentPage + 2) {
            html += '<span>...</span>';
        }
    }
    
    html += `
        <button onclick="load${capitalize(type)}(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
    
    container.innerHTML = html;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// ========================================
// Utility Functions
// ========================================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ========================================
// Initialize Application
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
});
