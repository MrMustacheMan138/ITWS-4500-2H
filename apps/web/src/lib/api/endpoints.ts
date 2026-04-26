import { apiClient } from './client';

// ── Auth ──────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string) {
  return apiClient('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function signup(email: string, password: string, name: string) {
  return apiClient('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: name }),
  });
}

// ── Programs ──────────────────────────────────────────────────────────────────

export async function getPrograms() {
  return apiClient('/api/v1/programs/');
}

export async function getProgram(id: number) {
  return apiClient(`/api/v1/programs/${id}`);
}

export async function createProgram(data: { name: string; institution?: string; description?: string }) {
  return apiClient('/api/v1/programs/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function deleteProgram(id: number) {
  return apiClient(`/api/v1/programs/${id}`, { method: 'DELETE' });
}

// ── Sources ───────────────────────────────────────────────────────────────────

export async function getSources(params?: { program_id?: number; status?: string }) {
  const qs = new URLSearchParams();
  if (params?.program_id !== undefined) qs.set('program_id', String(params.program_id));
  if (params?.status)                   qs.set('status', params.status);
  const query = qs.toString() ? `?${qs}` : '';
  return apiClient(`/api/v1/sources/${query}`);
}

export async function deleteSource(id: number) {
  return apiClient(`/api/v1/sources/${id}`, { method: 'DELETE' });
}

// ── Ingest ────────────────────────────────────────────────────────────────────

export async function ingestLink(programId: number, url: string) {
  return apiClient('/api/v1/ingest/link', {
    method: 'POST',
    body: JSON.stringify({ program_id: programId, url }),
  });
}

export async function ingestPdf(programId: number, file: File) {
  const form = new FormData();
  form.append('program_id', String(programId));
  form.append('file', file);
  // Don't set Content-Type — browser sets it with the boundary
  return apiClient('/api/v1/ingest/pdf', { method: 'POST', body: form, headers: {} });
}

// ── Comparisons ───────────────────────────────────────────────────────────────

export async function getComparisons() {
  return apiClient('/api/v1/comparisons/');
}

export async function createComparison(data: { title: string; program_a_id?: number; program_b_id?: number }) {
  return apiClient('/api/v1/comparisons/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getComparison(id: string | number) {
  return apiClient(`/api/v1/comparisons/${id}`);
}
