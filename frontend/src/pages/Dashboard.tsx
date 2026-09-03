import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, AlertTriangle, ShieldCheck } from 'lucide-react';
import api from '../api/client';

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['sla-compliance'],
    queryFn: async () => {
      const res = await api.get('/reports/sla-compliance?days=30');
      return res.data;
    }
  });

  const { data: escalations, isLoading: escLoading } = useQuery({
    queryKey: ['escalations'],
    queryFn: async () => {
      const res = await api.get('/escalations');
      return res.data;
    }
  });

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white tracking-tight">Manager Dashboard</h1>
          <p className="text-slate-400 mt-1">SLA Compliance & Escalations Overview</p>
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-500/10 text-blue-400 rounded-lg">
                <BarChart3 size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Total Tickets (30d)</p>
                <h3 className="text-2xl font-bold text-white mt-1">
                  {statsLoading ? '-' : stats?.total_tickets}
                </h3>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
                <ShieldCheck size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">First Response Met</p>
                <h3 className="text-2xl font-bold text-white mt-1">
                  {statsLoading ? '-' : `${stats?.first_response_met_percentage.toFixed(1)}%`}
                </h3>
              </div>
            </div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg">
                <ShieldCheck size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-slate-400">Resolution Met</p>
                <h3 className="text-2xl font-bold text-white mt-1">
                  {statsLoading ? '-' : `${stats?.resolution_met_percentage.toFixed(1)}%`}
                </h3>
              </div>
            </div>
          </div>
        </div>

        {/* Escalations Table */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="px-6 py-5 border-b border-slate-800 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <AlertTriangle className="text-amber-500" size={20} />
              Active Escalations
            </h2>
          </div>
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/30 border-b border-slate-800 text-slate-400 text-sm font-medium">
                <th className="px-6 py-4">Ticket ID</th>
                <th className="px-6 py-4">Reason</th>
                <th className="px-6 py-4">Escalated At</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {escLoading ? (
                 <tr><td colSpan={4} className="px-6 py-8 text-center text-slate-500">Loading escalations...</td></tr>
              ) : escalations?.filter((e: any) => !e.resolved_at).length === 0 ? (
                 <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-slate-500">
                    <ShieldCheck className="w-8 h-8 mx-auto mb-3 text-emerald-500/50" />
                    All clear! No active escalations.
                  </td>
                </tr>
              ) : (
                escalations?.filter((e: any) => !e.resolved_at).map((esc: any) => (
                  <tr key={esc.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-mono text-sm text-indigo-400">#{esc.ticket_id.split('-')[0]}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-500 border border-amber-500/20">
                        {esc.reason.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-400">
                      {new Date(esc.created_at).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors">
                        Resolve
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
