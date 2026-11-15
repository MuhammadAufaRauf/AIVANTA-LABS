export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export type EmployeeStatus = "active" | "inactive" | "busy";
export type Priority = "low" | "medium" | "high" | "urgent";
export type TaskStatus = "todo" | "in_progress" | "review" | "completed" | "cancelled";
export type ProjectStatus = "planned" | "active" | "on_hold" | "completed" | "cancelled";

export interface Department { id: number; name: string; description: string; employee_count: number; created_at: string; updated_at: string }
export interface Employee { id: number; name: string; position: string; department_id: number; department_name: string; description: string; system_instructions: string; ai_provider: string; ai_model: string; status: EmployeeStatus; created_at: string; updated_at: string }
export interface Task { id: number; title: string; description: string; assigned_employee_id: number | null; assigned_employee_name: string | null; project_id: number | null; project_name: string | null; priority: Priority; status: TaskStatus; due_date: string | null; created_at: string; updated_at: string }
export interface Project { id: number; name: string; description: string; start_date: string | null; deadline: string | null; status: ProjectStatus; priority: Priority; created_at: string; updated_at: string; employee_ids: number[]; employee_names: string[]; task_count: number; completed_task_count: number; progress_percent: number }
export interface DashboardStats { total_employees: number; active_employees: number; total_departments: number; total_tasks: number; completed_tasks: number; ongoing_projects: number }

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { ...(init?.body ? { "Content-Type": "application/json" } : {}), ...init?.headers },
      cache: "no-store",
    });
  } catch {
    throw new Error("Tidak dapat terhubung ke backend. Pastikan API berjalan di localhost:8000.");
  }
  if (!response.ok) {
    let message = `Permintaan gagal (${response.status})`;
    try {
      const body = await response.json() as { detail?: string };
      if (body.detail) message = body.detail;
    } catch { /* keep status message if response is not JSON */ }
    throw new Error(message);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function dateLabel(value: string | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("id-ID", { dateStyle: "medium" }).format(new Date(`${value.slice(0, 10)}T00:00:00`));
}
