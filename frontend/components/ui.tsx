import type { ReactNode } from "react";

export function PageHeader({ title, description, action }: { title: string; description: string; action?: ReactNode }) {
  return <header className="flex flex-wrap items-start justify-between gap-4"><div><h1 className="text-3xl font-semibold">{title}</h1><p className="mt-2 text-sm text-slate-400">{description}</p></div>{action}</header>;
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-[#1b2b40] bg-[#0d1a2b] p-5 ${className}`}>{children}</section>;
}

export function Notice({ children, error = false }: { children: ReactNode; error?: boolean }) {
  return <div role={error ? "alert" : "status"} className={`rounded-xl border px-4 py-3 text-sm ${error ? "border-rose-500/30 bg-rose-500/10 text-rose-200" : "border-[#1b2b40] bg-[#0d1a2b] text-slate-400"}`}>{children}</div>;
}

export function Button({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`rounded-lg bg-cyan-500 px-4 py-2 text-sm font-semibold text-[#06111e] transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50 ${props.className ?? ""}`}>{children}</button>;
}

export function SecondaryButton({ children, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return <button {...props} className={`rounded-lg border border-[#29415f] px-3 py-2 text-sm text-slate-200 hover:bg-white/5 disabled:opacity-50 ${props.className ?? ""}`}>{children}</button>;
}

export function StatusBadge({ value }: { value: string }) {
  const colors: Record<string, string> = {
    active: "bg-emerald-400/10 text-emerald-300", completed: "bg-emerald-400/10 text-emerald-300",
    busy: "bg-amber-400/10 text-amber-300", in_progress: "bg-blue-400/10 text-blue-300",
    review: "bg-violet-400/10 text-violet-300", inactive: "bg-slate-500/10 text-slate-400",
    cancelled: "bg-rose-400/10 text-rose-300", on_hold: "bg-amber-400/10 text-amber-300",
    todo: "bg-slate-500/10 text-slate-300", planned: "bg-cyan-400/10 text-cyan-200",
  };
  return <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${colors[value] ?? "bg-slate-500/10 text-slate-300"}`}>{value.replaceAll("_", " ")}</span>;
}

export function PriorityBadge({ value }: { value: string }) {
  const color = value === "urgent" ? "text-rose-300" : value === "high" ? "text-orange-300" : value === "medium" ? "text-amber-300" : "text-slate-400";
  return <span className={`text-sm font-medium capitalize ${color}`}>{value}</span>;
}

export const inputClass = "mt-1 w-full rounded-lg border border-[#29415f] bg-[#081525] px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-400";
export const labelClass = "block text-sm text-slate-300";
