import { notFound } from "next/navigation";
import { EmployeeDetailPage } from "@/components/management";
import { Shell } from "@/components/shell";

type Props = { params: Promise<{ id: string }> };

export default async function EmployeeDetailRoute({ params }: Props) {
  const { id } = await params;
  const employeeId = Number(id);
  if (!Number.isSafeInteger(employeeId) || employeeId < 1) notFound();
  return <Shell><EmployeeDetailPage id={employeeId} /></Shell>;
}
