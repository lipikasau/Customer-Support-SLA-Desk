import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Clock, Plus, AlertCircle, CheckCircle2 } from 'lucide-react';
import api from '../api/client';
import SlaBadge from '../components/SlaBadge';
import NewTicketModal from '../components/NewTicketModal';

interface Ticket {
  id: string;
  subject: string;
  priority: string;
  status: string;
  sla_first_response_due_at: string;
  sla_resolution_due_at: string;
  first_response_breached: boolean;
  resolution_breached: boolean;
  resolved_at: string | null;
}

export default function TicketList() {
  const [isModalOpen, setIsModalOpen] = React.useState(false);

  const { data: tickets, isLoading } = useQuery<Ticket[]>({
    queryKey: ['tickets'],
    queryFn: async () => {
      const res = await api.get('/tickets');
      return res.data;
    }
  });

  if (isLoading) return <div className="p-8 text-slate-400">Loading tickets...</div>;

  return (
    <div className="min-h-screen bg-slate-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Tickets</h1>
            <p className="text-slate-400 mt-1">Manage and track customer support requests.</p>
          </div>
          <button 
            onClick={() => setIsModalOpen(true)}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 shadow-lg shadow-indigo-500/25"
          >
            <Plus size={18} />
            New Ticket
          </button>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-800/50 border-b border-slate-800 text-slate-400 text-sm font-medium">
                <th className="px-6 py-4">Subject</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Priority</th>
                <th className="px-6 py-4">SLA Deadlines</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {tickets?.map(ticket => (
                <tr key={ticket.id} className="hover:bg-slate-800/30 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="text-slate-200 font-medium group-hover:text-indigo-400 transition-colors">
                      {ticket.subject}
                    </div>
                    <div className="text-slate-500 text-xs mt-1 font-mono">
                      #{ticket.id.split('-')[0]}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                      {ticket.status === 'resolved' ? <CheckCircle2 size={12} className="text-green-400" /> : <Clock size={12} />}
                      {ticket.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="capitalize text-slate-300 text-sm">{ticket.priority}</span>
                  </td>
                  <td className="px-6 py-4 space-y-2">
                    <div className="flex flex-col gap-2 items-start">
                      <SlaBadge 
                        dueAt={ticket.sla_first_response_due_at} 
                        isBreached={ticket.first_response_breached}
                        isResolved={ticket.status !== 'open'}
                        label="First Response" 
                      />
                      <SlaBadge 
                        dueAt={ticket.sla_resolution_due_at} 
                        isBreached={ticket.resolution_breached}
                        isResolved={!!ticket.resolved_at}
                        label="Resolution" 
                      />
                    </div>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link 
                      to={`/tickets/${ticket.id}`}
                      className="text-indigo-400 hover:text-indigo-300 font-medium text-sm transition-colors"
                    >
                      View details &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
              
              {!tickets?.length && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    <AlertCircle className="w-8 h-8 mx-auto mb-3 opacity-50" />
                    No tickets found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      {isModalOpen && <NewTicketModal onClose={() => setIsModalOpen(false)} />}
    </div>
  );
}
