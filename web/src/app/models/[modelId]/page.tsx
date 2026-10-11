import { ModelDetailPage } from "@/features/ModelDetailPage";

// Static export builds this page once with a placeholder; FastAPI serves it for
// any id and the page reads the real id from the URL (useRouteIds).
export const dynamicParams = false;

export function generateStaticParams() {
  return [{ modelId: "_" }];
}

export default function Page() {
  return <ModelDetailPage />;
}
