import { DashboardClient } from '@/components/DashboardClient';

export const metadata = {
  title: 'VC Outreach - Approvals Dashboard',
  description: 'Review and approve VC outreach cards',
};

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <DashboardClient />
      </div>
    </main>
  );
}