import { SessionPanel } from "@/features/auth/SessionPanel";
import { PrivateResourcesPanel } from "@/features/private-data/PrivateResourcesPanel";
import { PrivateUploadPanel } from "@/features/private-data/PrivateUploadPanel";

export default function AccountPage() {
  return <main><SessionPanel /><PrivateResourcesPanel /><PrivateUploadPanel /></main>;
}
