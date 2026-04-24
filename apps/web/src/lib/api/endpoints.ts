import { apiClient } from './client';

// Auth endpoints
export async function login(email: string, password: string) {
  const response = await apiClient('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return response;
}

export async function signup(email: string, password: string, name: string) {
  const response = await apiClient('/api/v1/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name: name }),
  });
  return response;
}

// Programs endpoints
export async function getPrograms() {
  const response = await apiClient('/api/v1/programs');
  return response;
}

// Comparison endpoints
export async function createComparison(data: any) {
  const response = await apiClient('/api/v1/comparisons', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response;
}

export async function getComparison(id: string) {
  const response = await apiClient(`/api/v1/comparisons/${id}`);
  return response;
}
