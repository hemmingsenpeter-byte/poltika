import { DatasetDetailPage } from "@/features/DatasetDetailPage";

// Static export builds this page once with a placeholder; FastAPI serves it for
// any id and the page reads the real id from the URL (useRouteIds).
export const dynamicParams = false;

export function generateStaticParams() {
  return [{ datasetId: "_" }];
}

export default function Page() {
  return <DatasetDetailPage />;
}
